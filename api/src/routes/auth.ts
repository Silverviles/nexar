import { Router } from 'express';
import type { Request, Response } from 'express';
import bcrypt from 'bcrypt';
import { OAuth2Client } from 'google-auth-library';
import { logger } from '@config/logger.js';
import { authMiddleware, generateToken } from '@middleware/auth.js';
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
} from '@/services/user-service.js';
import { sendVerificationEmail } from '@/services/email-service.js';

const router = Router();
const SALT_ROUNDS = 12;
// Requires min 8 chars, at least one uppercase, one lowercase, one digit, and one special character (!@#$%^&*()_+-=[]{};':"\\|,.<>/?)
const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]).{8,}$/;
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:5173';
const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID || '';
const GOOGLE_CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET || '';
const GOOGLE_REDIRECT_URI = `${FRONTEND_URL}/auth/google/callback`;

const googleClient = new OAuth2Client(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI);

// POST /api/v1/auth/register
router.post('/register', async (req: Request, res: Response) => {
  try {
    const { email, password, name } = req.body as {
      email?: string;
      password?: string;
      name?: string;
    };

    if (!email || !password || !name) {
      res.status(400).json({ error: 'Email, password, and name are required' });
      return;
    }

    if (!PASSWORD_REGEX.test(password)) {
      res.status(400).json({
        error:
          'Password must be at least 8 characters and include uppercase, lowercase, a number, and a special character (!@#$%^&* etc.)',
      });
      return;
    }

    const existingUser = await findUserByEmail(email);

    if (existingUser) {
      // If already verified, reject
      if (existingUser.emailVerified) {
        res.status(409).json({ error: 'An account with this email already exists' });
        return;
      }

      // If not verified, update and resend verification email
      const hashedPassword = await bcrypt.hash(password, SALT_ROUNDS);
      const verificationToken = await updateUnverifiedUser(existingUser.id, {
        name,
        hashedPassword,
      });

      await sendVerificationEmail(email, name, verificationToken);

      logger.info(`Re-registration for unverified user: ${email}`);
      res.status(200).json({
        message: 'A new verification email has been sent. Please check your inbox.',
      });
      return;
    }

    // Create new user
    const hashedPassword = await bcrypt.hash(password, SALT_ROUNDS);
    const { verificationToken } = await createUser({
      email,
      name,
      hashedPassword,
    });

    await sendVerificationEmail(email, name, verificationToken);

    logger.info(`New user registered: ${email}`);
    res.status(201).json({
      message: 'Account created. Please check your email to verify your account.',
    });
  } catch (error) {
    logger.error('Registration failed', { error });
    res.status(500).json({ error: 'Registration failed. Please try again.' });
  }
});

// POST /api/v1/auth/login
router.post('/login', async (req: Request, res: Response) => {
  try {
    const { email, password } = req.body as {
      email?: string;
      password?: string;
    };

    if (!email || !password) {
      res.status(400).json({ error: 'Email and password are required' });
      return;
    }

    const user = await findUserByEmail(email);

    if (!user || !user.hashedPassword) {
      res.status(401).json({ error: 'Invalid email or password' });
      return;
    }

    const passwordValid = await bcrypt.compare(password, user.hashedPassword);
    if (!passwordValid) {
      res.status(401).json({ error: 'Invalid email or password' });
      return;
    }

    if (!user.emailVerified) {
      res.status(403).json({
        error: 'Please verify your email before signing in',
        code: 'EMAIL_NOT_VERIFIED',
      });
      return;
    }

    const token = generateToken({
      userId: user.id,
      email: user.email,
      role: user.role,
    });

    logger.info(`User logged in: ${email}`);
    res.json({
      token,
      user: sanitizeUser(user),
    });
  } catch (error) {
    logger.error('Login failed', { error });
    res.status(500).json({ error: 'Login failed. Please try again.' });
  }
});

// POST /api/v1/auth/google
router.post('/google', async (req: Request, res: Response) => {
  try {
    const { code } = req.body as { code?: string };

    if (!code) {
      res.status(400).json({ error: 'Authorization code is required' });
      return;
    }

    // Exchange auth code for tokens
    const { tokens } = await googleClient.getToken(code);
    const idToken = tokens.id_token;

    if (!idToken) {
      res.status(400).json({ error: 'Failed to obtain ID token from Google' });
      return;
    }

    // Verify the ID token
    const ticket = await googleClient.verifyIdToken({
      idToken,
      audience: GOOGLE_CLIENT_ID,
    });

    const payload = ticket.getPayload();
    if (!payload?.email || !payload.sub) {
      res.status(400).json({ error: 'Invalid Google token payload' });
      return;
    }

    const googleId = payload.sub;
    const email = payload.email;
    const name = payload.name || email.split('@')[0] || 'User';

    // Check if user exists by Google ID
    let user = await findUserByGoogleId(googleId);

    if (!user) {
      // Check if user exists by email (registered via email/password)
      user = await findUserByEmail(email);

      if (user) {
        // Link Google account to existing user
        await linkGoogleAccount(user.id, googleId);
        user.googleId = googleId;
        user.emailVerified = true;
      } else {
        // Create new user (auto-verified via Google)
        user = await createGoogleUser({ email, name, googleId });
      }
    }

    const token = generateToken({
      userId: user.id,
      email: user.email,
      role: user.role,
    });

    logger.info(`Google login: ${email}`);
    res.json({
      token,
      user: sanitizeUser(user),
    });
  } catch (error) {
    logger.error('Google authentication failed', { error });
    res.status(500).json({ error: 'Google authentication failed. Please try again.' });
  }
});

// GET /api/v1/auth/verify-email?token=xxx
router.get('/verify-email', async (req: Request, res: Response) => {
  try {
    const { token } = req.query as { token?: string };

    if (!token) {
      res.redirect(`${FRONTEND_URL}/verify-email?status=error&message=Missing+verification+token`);
      return;
    }

    const user = await findUserByVerificationToken(token);

    if (!user) {
      res.redirect(`${FRONTEND_URL}/verify-email?status=error&message=Invalid+verification+link`);
      return;
    }

    if (user.emailVerified) {
      res.redirect(`${FRONTEND_URL}/verify-email?status=already-verified`);
      return;
    }

    if (isVerificationTokenExpired(user)) {
      res.redirect(
        `${FRONTEND_URL}/verify-email?status=expired&email=${encodeURIComponent(user.email)}`
      );
      return;
    }

    await markEmailVerified(user.id);

    logger.info(`Email verified: ${user.email}`);
    res.redirect(`${FRONTEND_URL}/verify-email?status=success`);
  } catch (error) {
    logger.error('Email verification failed', { error });
    res.redirect(`${FRONTEND_URL}/verify-email?status=error&message=Verification+failed`);
  }
});

// POST /api/v1/auth/resend-verification
router.post('/resend-verification', async (req: Request, res: Response) => {
  try {
    const { email } = req.body as { email?: string };

    if (!email) {
      res.status(400).json({ error: 'Email is required' });
      return;
    }

    const user = await findUserByEmail(email);

    if (!user) {
      // Don't reveal whether the email exists
      res.json({ message: 'If an account exists with this email, a verification link has been sent.' });
      return;
    }

    if (user.emailVerified) {
      res.json({ message: 'If an account exists with this email, a verification link has been sent.' });
      return;
    }

    const newToken = await refreshVerificationToken(user.id);
    await sendVerificationEmail(user.email, user.name, newToken);

    logger.info(`Verification email resent to: ${email}`);
    res.json({ message: 'If an account exists with this email, a verification link has been sent.' });
  } catch (error) {
    logger.error('Resend verification failed', { error });
    res.status(500).json({ error: 'Failed to resend verification email. Please try again.' });
  }
});

// GET /api/v1/auth/me (protected)
router.get('/me', authMiddleware, async (req: Request, res: Response) => {
  try {
    const user = await findUserById(req.user!.userId);

    if (!user) {
      res.status(404).json({ error: 'User not found' });
      return;
    }

    res.json({ user: sanitizeUser(user) });
  } catch (error) {
    logger.error('Failed to fetch user', { error });
    res.status(500).json({ error: 'Failed to fetch user data' });
  }
});

export default router;
