import type { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { logger } from '@config/logger.js';

const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret-change-me';
const JWT_EXPIRES_IN = '7d';

if (process.env.NODE_ENV === 'production' && JWT_SECRET === 'dev-secret-change-me') {
  logger.error('CRITICAL: Insecure default JWT_SECRET detected in production environment. Server will not start.', {
    action: 'startup_abort',
  });
  throw new Error('JWT_SECRET must be configured with a strong value in production.');
}

logger.debug("Auth middleware initialized", {
  jwtExpiresIn: JWT_EXPIRES_IN,
  secretConfigured: JWT_SECRET !== 'dev-secret-change-me',
});

export interface JwtPayload {
  userId: string;
  email: string;
  role: string;
}

declare global {
  namespace Express {
    interface Request {
      user?: JwtPayload;
    }
  }
}

export function generateToken(payload: JwtPayload): string {
  logger.debug("Generating JWT token", {
    userId: payload.userId,
    email: payload.email,
    role: payload.role,
    expiresIn: JWT_EXPIRES_IN,
  });

  const token = jwt.sign(payload, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });

  logger.debug("JWT token generated successfully", {
    userId: payload.userId,
    tokenLength: token.length,
  });

  return token;
}

export function authMiddleware(req: Request, res: Response, next: NextFunction): void {
  const requestId = req.requestId;
  const authHeader = req.headers.authorization;

  logger.debug("Auth middleware invoked", {
    requestId,
    path: req.originalUrl,
    method: req.method,
    hasAuthHeader: !!authHeader,
    authHeaderPrefix: authHeader ? authHeader.substring(0, 7) : undefined,
  });

  if (!authHeader?.startsWith('Bearer ')) {
    logger.warn('Authentication failed: missing or malformed authorization header', {
      requestId,
      path: req.originalUrl,
      method: req.method,
      hasAuthHeader: !!authHeader,
      ip: (req.headers['x-forwarded-for'] as string)?.split(',')[0]?.trim() || req.ip || 'unknown',
    });
    res.status(401).json({ error: 'Missing or invalid authorization header' });
    return;
  }

  const token = authHeader.slice(7);

  logger.debug("Attempting JWT verification", {
    requestId,
    tokenLength: token.length,
  });

  try {
    const decoded = jwt.verify(token, JWT_SECRET) as JwtPayload;
    req.user = decoded;

    logger.info('Authentication successful', {
      requestId,
      userId: decoded.userId,
      email: decoded.email,
      role: decoded.role,
      path: req.originalUrl,
    });

    logger.debug('JWT payload decoded', {
      requestId,
      userId: decoded.userId,
      email: decoded.email,
      role: decoded.role,
    });

    next();
  } catch (error) {
    // Categorize the JWT error for more useful logging
    let errorType = 'unknown';
    if (error instanceof jwt.TokenExpiredError) {
      errorType = 'token_expired';
    } else if (error instanceof jwt.JsonWebTokenError) {
      errorType = 'invalid_token';
    } else if (error instanceof jwt.NotBeforeError) {
      errorType = 'token_not_active';
    }

    logger.warn('Authentication failed: invalid JWT token', {
      requestId,
      errorType,
      path: req.originalUrl,
      method: req.method,
      ip: (req.headers['x-forwarded-for'] as string)?.split(',')[0]?.trim() || req.ip || 'unknown',
      error: error instanceof Error ? error.message : String(error),
    });

    res.status(401).json({ error: 'Invalid or expired token' });
  }
}
