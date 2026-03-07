import type { Request, Response, NextFunction } from "express";
import crypto from "crypto";
import { logger } from "@config/logger.js";

// ---------------------------------------------------------------------------
// Thresholds
// ---------------------------------------------------------------------------
const SLOW_RESPONSE_THRESHOLD_MS = 5_000;

// ---------------------------------------------------------------------------
// Extend Express Request to carry a unique request ID
// ---------------------------------------------------------------------------
declare global {
  namespace Express {
    interface Request {
      requestId?: string;
    }
  }
}

// ---------------------------------------------------------------------------
// Helper – mask sensitive header values
// ---------------------------------------------------------------------------
const SENSITIVE_HEADERS = new Set(["authorization", "cookie", "x-api-key"]);

function safeHeaders(headers: Record<string, unknown>): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(headers)) {
    if (SENSITIVE_HEADERS.has(key.toLowerCase())) {
      out[key] = "[REDACTED]";
    } else {
      out[key] = value;
    }
  }
  return out;
}

// ---------------------------------------------------------------------------
// Middleware
// ---------------------------------------------------------------------------

/**
 * Global request / response logger.
 *
 * Runs on every incoming HTTP request and logs:
 *   - INFO  : request received  (method, path, IP, user-agent, content-length)
 *   - DEBUG : full headers (sensitive values redacted) and body size
 *   - INFO  : response completed (status, duration)
 *   - WARN  : slow responses (> SLOW_RESPONSE_THRESHOLD_MS)
 *   - WARN  : 4xx client errors
 *   - ERROR : 5xx server errors
 *
 * Generates a UUID `requestId` and attaches it to `req.requestId` so that
 * all downstream logs can include it for correlation.
 */
export function requestLoggerMiddleware(
  req: Request,
  res: Response,
  next: NextFunction,
): void {
  const requestId = crypto.randomUUID();
  req.requestId = requestId;

  const startTime = Date.now();

  // ---- Incoming request ----
  const ip =
    (req.headers["x-forwarded-for"] as string)?.split(",")[0]?.trim() ||
    req.ip ||
    req.socket.remoteAddress ||
    "unknown";

  logger.info("Incoming request", {
    requestId,
    method: req.method,
    path: req.originalUrl,
    ip,
    userAgent: req.headers["user-agent"] || "unknown",
    contentLength: req.headers["content-length"] || 0,
  });

  logger.debug("Request details", {
    requestId,
    method: req.method,
    path: req.originalUrl,
    headers: safeHeaders(req.headers as Record<string, unknown>),
    query: req.query,
    bodySize: req.body ? JSON.stringify(req.body).length : 0,
    protocol: req.protocol,
    hostname: req.hostname,
  });

  // ---- Hook into response finish to log completion ----
  res.on("finish", () => {
    const durationMs = Date.now() - startTime;
    const statusCode = res.statusCode;

    const meta = {
      requestId,
      method: req.method,
      path: req.originalUrl,
      statusCode,
      durationMs,
      ip,
      userId: req.user?.userId || undefined,
    };

    // Always log the response at INFO level
    logger.info("Request completed", meta);

    // Additional severity-based logging
    if (statusCode >= 500) {
      logger.error("Server error response", meta);
    } else if (statusCode >= 400) {
      logger.warn("Client error response", {
        ...meta,
        userAgent: req.headers["user-agent"],
      });
    }

    // Slow response warning
    if (durationMs > SLOW_RESPONSE_THRESHOLD_MS) {
      logger.warn("Slow response detected", {
        ...meta,
        threshold: SLOW_RESPONSE_THRESHOLD_MS,
      });
    }

    logger.debug("Response details", {
      requestId,
      statusCode,
      durationMs,
      responseHeaders: {
        contentType: res.getHeader("content-type"),
        contentLength: res.getHeader("content-length"),
      },
    });
  });

  next();
}
