import { Router } from "express";
import type { Request, Response } from "express";
import bcrypt from "bcrypt";
import { OAuth2Client } from "google-auth-library";
import { logger } from "@config/logger.js";
import { authMiddleware, generateToken } from "@middleware/auth.js";
import {
  findUserByEmail,
  findUserById,
  findUserByGoogleId,
  findUserByVerificationToken,
  createUser,
  createGoogleUser,
  updateUnverifiedUser,
  markEmailVerified,
  refreshVerificationToken,
  linkGoogleAccount,
  isVerificationTokenExpired,
  sanitizeUser,
} from "@/services/user-service.js";
import { sendVerificationEmail } from "@/services/email-service.js";

const router = Router();
const SALT_ROUNDS = 12;
// Requires min 8 chars, at least one uppercase, one lowercase, one digit, and one special character (!@#$%^&*()_+-=[]{};':"\\|,.<>/?)
const PASSWORD_REGEX =
  /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]).{8,}$/;
const FRONTEND_URL = process.env.FRONTEND_URL || "http://localhost:5173";
const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID || "";
const GOOGLE_CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET || "";
const GOOGLE_REDIRECT_URI = `${FRONTEND_URL}/auth/google/callback`;

const googleClient = new OAuth2Client(
  GOOGLE_CLIENT_ID,
  GOOGLE_CLIENT_SECRET,
  GOOGLE_REDIRECT_URI,
);

logger.debug("Auth routes initialized", {
  frontendUrl: FRONTEND_URL,
  googleClientConfigured: !!GOOGLE_CLIENT_ID,
  googleRedirectUri: GOOGLE_REDIRECT_URI,
  saltRounds: SALT_ROUNDS,
});

// ============================================================================
// POST /api/v1/auth/register
// ============================================================================
router.post("/register", async (req: Request, res: Response) => {
  const requestId = req.requestId;
  logger.info("Registration attempt started", { requestId });

  try {
    const { email, password, name } = req.body as {
      email?: string;
      password?: string;
      name?: string;
    };

    logger.debug("Registration request body parsed", {
      requestId,
      hasEmail: !!email,
      hasPassword: !!password,
      hasName: !!name,
      emailValue: email || undefined,
      nameValue: name || undefined,
      // Never log the password itself
    });

    if (!email || !password || !name) {
      logger.warn("Registration failed: missing required fields", {
        requestId,
        missingFields: [
          !email && "email",
          !password && "password",
          !name && "name",
        ].filter(Boolean),
      });
      res.status(400).json({ error: "Email, password, and name are required" });
      return;
    }

    logger.debug("Validating password strength", { requestId, email });

    if (!PASSWORD_REGEX.test(password)) {
      logger.warn("Registration failed: password does not meet requirements", {
        requestId,
        email,
        passwordLength: password.length,
      });
      res.status(400).json({
        error:
          "Password must be at least 8 characters and include uppercase, lowercase, a number, and a special character (!@#$%^&* etc.)",
      });
      return;
    }

    logger.debug("Password validation passed, checking for existing user", {
      requestId,
      email,
    });

    const existingUser = await findUserByEmail(email);

    if (existingUser) {
      logger.debug("Existing user found during registration", {
        requestId,
        email,
        existingUserId: existingUser.id,
        emailVerified: existingUser.emailVerified,
      });

      // If already verified, reject
      if (existingUser.emailVerified) {
        logger.warn("Registration rejected: duplicate email (verified account exists)", {
          requestId,
          email,
        });
        res
          .status(409)
          .json({ error: "An account with this email already exists" });
        return;
      }

      // If not verified, update and resend verification email
      logger.info("Re-registration for unverified user, updating credentials", {
        requestId,
        email,
        userId: existingUser.id,
      });

      logger.debug("Hashing password for re-registration", { requestId, email, saltRounds: SALT_ROUNDS });
      const hashStart = Date.now();
      const hashedPassword = await bcrypt.hash(password, SALT_ROUNDS);
      logger.debug("Password hashed successfully", {
        requestId,
        email,
        hashDurationMs: Date.now() - hashStart,
      });

      const verificationToken = await updateUnverifiedUser(existingUser.id, {
        name,
        hashedPassword,
      });

      logger.debug("Unverified user updated, sending verification email", {
        requestId,
        email,
        userId: existingUser.id,
      });

      await sendVerificationEmail(email, name, verificationToken);

      logger.info("Re-registration completed: verification email resent", {
        requestId,
        email,
        userId: existingUser.id,
      });
      res.status(200).json({
        message:
          "A new verification email has been sent. Please check your inbox.",
      });
      return;
    }

    logger.debug("No existing user found, creating new account", {
      requestId,
      email,
    });

    // Create new user
    logger.debug("Hashing password for new user", { requestId, email, saltRounds: SALT_ROUNDS });
    const hashStart = Date.now();
    const hashedPassword = await bcrypt.hash(password, SALT_ROUNDS);
    logger.debug("Password hashed successfully", {
      requestId,
      email,
      hashDurationMs: Date.now() - hashStart,
    });

    const { verificationToken } = await createUser({
      email,
      name,
      hashedPassword,
    });

    logger.debug("User created in database, sending verification email", {
      requestId,
      email,
    });

    await sendVerificationEmail(email, name, verificationToken);

    logger.info("New user registered successfully", {
      requestId,
      email,
      name,
    });
    res.status(201).json({
      message:
        "Account created. Please check your email to verify your account.",
    });
  } catch (error) {
    logger.error("Registration failed with unexpected error", {
      requestId,
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
    });
    res.status(500).json({ error: "Registration failed. Please try again." });
  }
});

// ============================================================================
// POST /api/v1/auth/login
// ============================================================================
router.post("/login", async (req: Request, res: Response) => {
  const requestId = req.requestId;
  logger.info("Login attempt started", { requestId });

  try {
    const { email, password } = req.body as {
      email?: string;
      password?: string;
    };

    logger.debug("Login request body parsed", {
      requestId,
      hasEmail: !!email,
      hasPassword: !!password,
      emailValue: email || undefined,
    });

    if (!email || !password) {
      logger.warn("Login failed: missing required fields", {
        requestId,
        missingFields: [
          !email && "email",
          !password && "password",
        ].filter(Boolean),
      });
      res.status(400).json({ error: "Email and password are required" });
      return;
    }

    logger.debug("Looking up user by email", { requestId, email });
    const user = await findUserByEmail(email);

    if (!user || !user.hashedPassword) {
      logger.warn("Login failed: user not found or no password set", {
        requestId,
        email,
        userExists: !!user,
        hasPassword: user ? !!user.hashedPassword : false,
      });
      res.status(401).json({ error: "Invalid email or password" });
      return;
    }

    logger.debug("User found, comparing password", {
      requestId,
      email,
      userId: user.id,
    });

    const compareStart = Date.now();
    const passwordValid = await bcrypt.compare(password, user.hashedPassword);
    logger.debug("Password comparison completed", {
      requestId,
      email,
      valid: passwordValid,
      compareDurationMs: Date.now() - compareStart,
    });

    if (!passwordValid) {
      logger.warn("Login failed: invalid password", {
        requestId,
        email,
        userId: user.id,
        ip: (req.headers['x-forwarded-for'] as string)?.split(',')[0]?.trim() || req.ip || 'unknown',
      });
      res.status(401).json({ error: "Invalid email or password" });
      return;
    }

    if (!user.emailVerified) {
      logger.warn("Login failed: email not verified", {
        requestId,
        email,
        userId: user.id,
      });
      res.status(403).json({
        error: "Please verify your email before signing in",
        code: "EMAIL_NOT_VERIFIED",
      });
      return;
    }

    logger.debug("Generating JWT token for user", {
      requestId,
      userId: user.id,
      email: user.email,
      role: user.role,
    });

    const token = generateToken({
      userId: user.id,
      email: user.email,
      role: user.role,
    });

    logger.info("User logged in successfully", {
      requestId,
      email,
      userId: user.id,
      role: user.role,
    });

    res.json({
      token,
      user: sanitizeUser(user),
    });
  } catch (error) {
    logger.error("Login failed with unexpected error", {
      requestId,
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
    });
    res.status(500).json({ error: "Login failed. Please try again." });
  }
});

// ============================================================================
// POST /api/v1/auth/google
// ============================================================================
router.post("/google", async (req: Request, res: Response) => {
  const requestId = req.requestId;
  logger.info("Google OAuth login attempt started", { requestId });

  try {
    const { code } = req.body as { code?: string };

    logger.debug("Google OAuth request body parsed", {
      requestId,
      hasCode: !!code,
      codeLength: code ? code.length : 0,
    });

    if (!code) {
      logger.warn("Google OAuth failed: missing authorization code", {
        requestId,
      });
      res.status(400).json({ error: "Authorization code is required" });
      return;
    }

    // Exchange auth code for tokens
    logger.debug("Exchanging authorization code for tokens with Google", {
      requestId,
    });
    const tokenExchangeStart = Date.now();
    const { tokens } = await googleClient.getToken(code);
    logger.debug("Google token exchange completed", {
      requestId,
      durationMs: Date.now() - tokenExchangeStart,
      hasIdToken: !!tokens.id_token,
      hasAccessToken: !!tokens.access_token,
    });

    const idToken = tokens.id_token;

    if (!idToken) {
      logger.warn("Google OAuth failed: no ID token received from Google", {
        requestId,
      });
      res.status(400).json({ error: "Failed to obtain ID token from Google" });
      return;
    }

    // Verify the ID token
    logger.debug("Verifying Google ID token", { requestId });
    const verifyStart = Date.now();
    const ticket = await googleClient.verifyIdToken({
      idToken,
      audience: GOOGLE_CLIENT_ID,
    });
    logger.debug("Google ID token verified", {
      requestId,
      verifyDurationMs: Date.now() - verifyStart,
    });

    const payload = ticket.getPayload();
    if (!payload?.email || !payload.sub) {
      logger.warn("Google OAuth failed: invalid token payload (missing email or sub)", {
        requestId,
        hasEmail: !!payload?.email,
        hasSub: !!payload?.sub,
      });
      res.status(400).json({ error: "Invalid Google token payload" });
      return;
    }

    const googleId = payload.sub;
    const email = payload.email;
    const name = payload.name || email.split("@")[0] || "User";

    logger.debug("Google payload extracted", {
      requestId,
      email,
      name,
      googleIdPrefix: googleId.substring(0, 6) + "...",
    });

    // Check if user exists by Google ID
    logger.debug("Looking up user by Google ID", { requestId, email });
    let user = await findUserByGoogleId(googleId);

    if (!user) {
      logger.debug("No user found by Google ID, checking by email", {
        requestId,
        email,
      });

      // Check if user exists by email (registered via email/password)
      user = await findUserByEmail(email);

      if (user) {
        // Link Google account to existing user
        logger.info("Linking Google account to existing user", {
          requestId,
          email,
          userId: user.id,
        });
        await linkGoogleAccount(user.id, googleId);
        user.googleId = googleId;
        user.emailVerified = true;
        logger.debug("Google account linked successfully", {
          requestId,
          userId: user.id,
        });
      } else {
        // Create new user (auto-verified via Google)
        logger.info("Creating new user via Google OAuth", {
          requestId,
          email,
          name,
        });
        user = await createGoogleUser({ email, name, googleId });
        logger.debug("Google user created", {
          requestId,
          userId: user.id,
          email,
        });
      }
    } else {
      logger.debug("Existing user found by Google ID", {
        requestId,
        userId: user.id,
        email: user.email,
      });
    }

    logger.debug("Generating JWT token for Google user", {
      requestId,
      userId: user.id,
      email: user.email,
    });

    const token = generateToken({
      userId: user.id,
      email: user.email,
      role: user.role,
    });

    logger.info("Google OAuth login successful", {
      requestId,
      email,
      userId: user.id,
      isNewUser: !user.createdAt, // approximate — newly created won't have stale createdAt
    });

    res.json({
      token,
      user: sanitizeUser(user),
    });
  } catch (error) {
    logger.error("Google authentication failed with unexpected error", {
      requestId,
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
    });
    res
      .status(500)
      .json({ error: "Google authentication failed. Please try again." });
  }
});

// ============================================================================
// GET /api/v1/auth/verify-email?token=xxx
// ============================================================================
router.get("/verify-email", async (req: Request, res: Response) => {
  const requestId = req.requestId;
  logger.info("Email verification attempt started", { requestId });

  try {
    const { token } = req.query as { token?: string };

    logger.debug("Verification request parsed", {
      requestId,
      hasToken: !!token,
      tokenLength: token ? token.length : 0,
    });

    if (!token) {
      logger.warn("Email verification failed: missing verification token", {
        requestId,
      });
      res.redirect(
        `${FRONTEND_URL}/verify-email?status=error&message=Missing+verification+token`,
      );
      return;
    }

    logger.debug("Looking up user by verification token", { requestId });
    const user = await findUserByVerificationToken(token);

    if (!user) {
      logger.warn("Email verification failed: invalid verification token (no matching user)", {
        requestId,
      });
      res.redirect(
        `${FRONTEND_URL}/verify-email?status=error&message=Invalid+verification+link`,
      );
      return;
    }

    logger.debug("User found for verification token", {
      requestId,
      userId: user.id,
      email: user.email,
      emailVerified: user.emailVerified,
    });

    if (user.emailVerified) {
      logger.warn("Email verification skipped: email already verified", {
        requestId,
        userId: user.id,
        email: user.email,
      });
      res.redirect(`${FRONTEND_URL}/verify-email?status=already-verified`);
      return;
    }

    logger.debug("Checking verification token expiry", {
      requestId,
      userId: user.id,
    });

    if (isVerificationTokenExpired(user)) {
      logger.warn("Email verification failed: verification token expired", {
        requestId,
        userId: user.id,
        email: user.email,
      });
      res.redirect(
        `${FRONTEND_URL}/verify-email?status=expired&email=${encodeURIComponent(user.email)}`,
      );
      return;
    }

    logger.debug("Token is valid, marking email as verified", {
      requestId,
      userId: user.id,
      email: user.email,
    });

    await markEmailVerified(user.id);

    logger.info("Email verified successfully", {
      requestId,
      userId: user.id,
      email: user.email,
    });
    res.redirect(`${FRONTEND_URL}/verify-email?status=success`);
  } catch (error) {
    logger.error("Email verification failed with unexpected error", {
      requestId,
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
    });
    res.redirect(
      `${FRONTEND_URL}/verify-email?status=error&message=Verification+failed`,
    );
  }
});

// ============================================================================
// POST /api/v1/auth/resend-verification
// ============================================================================
router.post("/resend-verification", async (req: Request, res: Response) => {
  const requestId = req.requestId;
  logger.info("Resend verification email attempt started", { requestId });

  try {
    const { email } = req.body as { email?: string };

    logger.debug("Resend verification request body parsed", {
      requestId,
      hasEmail: !!email,
      emailValue: email || undefined,
    });

    if (!email) {
      logger.warn("Resend verification failed: missing email field", {
        requestId,
      });
      res.status(400).json({ error: "Email is required" });
      return;
    }

    logger.debug("Looking up user by email for resend verification", {
      requestId,
      email,
    });

    const user = await findUserByEmail(email);

    if (!user) {
      // Don't reveal whether the email exists — but log it internally
      logger.debug("Resend verification: no account found for email (returning generic response)", {
        requestId,
        email,
      });
      res.json({
        message:
          "If an account exists with this email, a verification link has been sent.",
      });
      return;
    }

    if (user.emailVerified) {
      logger.debug("Resend verification: account already verified (returning generic response)", {
        requestId,
        email,
        userId: user.id,
      });
      res.json({
        message:
          "If an account exists with this email, a verification link has been sent.",
      });
      return;
    }

    logger.debug("Refreshing verification token", {
      requestId,
      email,
      userId: user.id,
    });

    const newToken = await refreshVerificationToken(user.id);

    logger.debug("Verification token refreshed, sending email", {
      requestId,
      email,
      userId: user.id,
    });

    await sendVerificationEmail(user.email, user.name, newToken);

    logger.info("Verification email resent successfully", {
      requestId,
      email,
      userId: user.id,
    });
    res.json({
      message:
        "If an account exists with this email, a verification link has been sent.",
    });
  } catch (error) {
    logger.error("Resend verification failed with unexpected error", {
      requestId,
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
    });
    res.status(500).json({
      error: "Failed to resend verification email. Please try again.",
    });
  }
});

// ============================================================================
// GET /api/v1/auth/me (protected)
// ============================================================================
router.get("/me", authMiddleware, async (req: Request, res: Response) => {
  const requestId = req.requestId;
  logger.info("Fetch current user profile", {
    requestId,
    userId: req.user!.userId,
  });

  try {
    logger.debug("Looking up user by ID from JWT", {
      requestId,
      userId: req.user!.userId,
    });

    const user = await findUserById(req.user!.userId);

    if (!user) {
      logger.warn("User profile fetch failed: user not found for valid JWT token", {
        requestId,
        userId: req.user!.userId,
        email: req.user!.email,
      });
      res.status(404).json({ error: "User not found" });
      return;
    }

    logger.debug("User profile retrieved successfully", {
      requestId,
      userId: user.id,
      email: user.email,
      role: user.role,
    });

    logger.info("User profile returned", {
      requestId,
      userId: user.id,
    });

    res.json({ user: sanitizeUser(user) });
  } catch (error) {
    logger.error("Failed to fetch user profile with unexpected error", {
      requestId,
      userId: req.user?.userId,
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
    });
    res.status(500).json({ error: "Failed to fetch user data" });
  }
});

export default router;
