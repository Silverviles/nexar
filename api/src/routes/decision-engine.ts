import { Router, type Request, type Response } from "express";
import axios from "axios";
import { logger } from "@config/logger.js";
import {
  logDecision,
  getDecisionHistory,
  getDecisionById,
  submitFeedback,
  getAccuracyStats,
  getDashboardStats,
  type FeedbackInput,
} from "@/services/decision-log-service.js";

const router = Router();
const DECISION_ENGINE_URL =
  process.env.DECISION_ENGINE_URL || "http://localhost:8003";
const REQUEST_TIMEOUT = 30_000;
const SLOW_UPSTREAM_THRESHOLD_MS = 5_000;

logger.debug("Decision Engine routes initialized", {
  targetUrl: DECISION_ENGINE_URL,
  timeoutMs: REQUEST_TIMEOUT,
});

/**
 * Categorize axios/network errors into actionable types.
 */
function categorizeError(error: any): { errorType: string; detail: string } {
  if (error.code === "ECONNREFUSED") {
    return {
      errorType: "connection_refused",
      detail: "Decision Engine service is not running or not reachable",
    };
  }
  if (error.code === "ETIMEDOUT" || error.code === "ECONNABORTED") {
    return {
      errorType: "timeout",
      detail: `Request timed out after ${REQUEST_TIMEOUT}ms`,
    };
  }
  if (error.code === "ENOTFOUND") {
    return {
      errorType: "dns_failure",
      detail: "Could not resolve Decision Engine hostname",
    };
  }
  if (error.code === "ECONNRESET") {
    return {
      errorType: "connection_reset",
      detail: "Connection was reset by the upstream service",
    };
  }
  return {
    errorType: "network_error",
    detail: error.message || "Unknown network error",
  };
}

// ─────────────────────────────────────────────
//  Generic proxy handler (for health, model-info)
// ─────────────────────────────────────────────

const forwardRequest = async (req: Request, res: Response) => {
  const requestId = req.requestId;
  const targetUrl = `${DECISION_ENGINE_URL}/api/v1/decision-engine${req.path}`;

  logger.info(`[Decision Engine] Proxying request`, {
    requestId,
    method: req.method,
    originalUrl: req.originalUrl,
    targetUrl,
  });

  logger.debug("[Decision Engine] Upstream request details", {
    requestId,
    method: req.method,
    targetUrl,
    bodySize: req.body ? JSON.stringify(req.body).length : 0,
    contentType: req.headers["content-type"] || "application/json",
    queryParams: req.query,
    timeoutMs: REQUEST_TIMEOUT,
  });

  const startTime = Date.now();

  try {
    const response = await axios({
      method: req.method,
      url: targetUrl,
      data: req.body,
      params: req.query,
      headers: {
        "Content-Type": req.headers["content-type"] || "application/json",
      },
      timeout: REQUEST_TIMEOUT,
      validateStatus: () => true, // Accept all status codes
    });

    const durationMs = Date.now() - startTime;
    const responseBodySize = response.data
      ? JSON.stringify(response.data).length
      : 0;

    logger.info(`[Decision Engine] Upstream response received`, {
      requestId,
      statusCode: response.status,
      durationMs,
      responseBodySize,
      originalUrl: req.originalUrl,
    });

    logger.debug("[Decision Engine] Upstream response details", {
      requestId,
      statusCode: response.status,
      statusText: response.statusText,
      durationMs,
      responseBodySize,
      responseContentType: response.headers["content-type"],
    });

    // Warn on non-2xx upstream responses
    if (response.status >= 500) {
      logger.error("[Decision Engine] Upstream returned server error", {
        requestId,
        statusCode: response.status,
        targetUrl,
        durationMs,
        responsePreview: JSON.stringify(response.data).substring(0, 500),
      });
    } else if (response.status >= 400) {
      logger.warn("[Decision Engine] Upstream returned client error", {
        requestId,
        statusCode: response.status,
        targetUrl,
        durationMs,
        responsePreview: JSON.stringify(response.data).substring(0, 500),
      });
    }

    // Warn on slow responses
    if (durationMs > SLOW_UPSTREAM_THRESHOLD_MS) {
      logger.warn("[Decision Engine] Slow upstream response", {
        requestId,
        durationMs,
        threshold: SLOW_UPSTREAM_THRESHOLD_MS,
        targetUrl,
      });
    }

    logger.debug("[Decision Engine] Forwarding response to client", {
      requestId,
      statusCode: response.status,
    });

    // Forward the response
    res.status(response.status).json(response.data);
  } catch (error: any) {
    const durationMs = Date.now() - startTime;
    const { errorType, detail } = categorizeError(error);

    logger.error("[Decision Engine] Upstream request failed", {
      requestId,
      errorType,
      detail,
      errorCode: error.code,
      errorMessage: error.message,
      targetUrl,
      method: req.method,
      durationMs,
    });

    res.status(503).json({
      error: "Decision Engine service unavailable",
      message: error.message,
    });
  }
};

// ─────────────────────────────────────────────
//  POST /predict — proxy + log to Firestore
// ─────────────────────────────────────────────

router.post("/predict", async (req: Request, res: Response) => {
  const requestId = req.requestId;
  const targetUrl = `${DECISION_ENGINE_URL}/api/v1/decision-engine/predict`;
  const userId = (req as any).user?.userId || "anonymous";
  const budgetLimitUsd = req.query.budget_limit_usd
    ? parseFloat(req.query.budget_limit_usd as string)
    : undefined;

  logger.info("[Decision Engine] Predict request (with logging)", {
    requestId,
    userId,
    targetUrl,
    budgetLimitUsd,
  });

  const startTime = Date.now();

  try {
    // Forward to decision-engine
    const response = await axios({
      method: "POST",
      url: targetUrl,
      data: req.body,
      params: req.query,
      headers: {
        "Content-Type": req.headers["content-type"] || "application/json",
      },
      timeout: REQUEST_TIMEOUT,
      validateStatus: () => true,
    });

    const durationMs = Date.now() - startTime;

    logger.info("[Decision Engine] Predict upstream response", {
      requestId,
      statusCode: response.status,
      durationMs,
    });

    // If successful, log to Firestore
    let decisionId: string | null = null;
    if (response.status === 200 && response.data?.success) {
      try {
        decisionId = await logDecision({
          userId,
          requestBody: req.body,
          responseBody: response.data,
          ...(budgetLimitUsd !== undefined && { budgetLimitUsd }),
        });
        logger.info("[Decision Engine] Decision logged to Firestore", {
          requestId,
          decisionId,
        });
      } catch (logError: any) {
        // Don't fail the request if logging fails
        logger.error("[Decision Engine] Failed to log decision to Firestore", {
          requestId,
          error: logError.message,
        });
      }
    }

    // Return response with decision_id appended
    const responseData = {
      ...response.data,
      decision_id: decisionId,
    };

    res.status(response.status).json(responseData);
  } catch (error: any) {
    const durationMs = Date.now() - startTime;
    const { errorType, detail } = categorizeError(error);

    logger.error("[Decision Engine] Predict request failed", {
      requestId,
      errorType,
      detail,
      durationMs,
    });

    res.status(503).json({
      error: "Decision Engine service unavailable",
      message: error.message,
    });
  }
});

// ─────────────────────────────────────────────
//  GET /history — decision log history
// ─────────────────────────────────────────────

router.get("/history", async (req: Request, res: Response) => {
  const userId = (req as any).user?.userId;
  if (!userId) {
    return res.status(401).json({ error: "Authentication required" });
  }

  const limit = Math.min(parseInt(req.query.limit as string) || 20, 100);
  const offset = parseInt(req.query.offset as string) || 0;
  const hardware = req.query.hardware as string | undefined;
  const status = req.query.status as string | undefined;

  logger.info("[Decision Engine] Fetching history", {
    userId,
    limit,
    offset,
    hardware,
    status,
  });

  try {
    const filters: { hardware?: string; status?: string } = {};
    if (hardware) filters.hardware = hardware;
    if (status) filters.status = status;

    const result = await getDecisionHistory(userId, limit, offset, filters);

    // Serialize Firestore Timestamps to ISO strings
    const serialized = result.decisions.map((d: any) => ({
      ...d,
      createdAt: d.createdAt?.toDate?.()
        ? d.createdAt.toDate().toISOString()
        : d.createdAt,
      updatedAt: d.updatedAt?.toDate?.()
        ? d.updatedAt.toDate().toISOString()
        : d.updatedAt,
    }));

    res.json({
      decisions: serialized,
      total: result.total,
      limit,
      offset,
      hasMore: offset + limit < result.total,
    });
  } catch (error: any) {
    logger.error("[Decision Engine] Failed to fetch history", {
      userId,
      error: error.message,
    });
    res.status(500).json({
      error: "Failed to fetch decision history",
      message: error.message,
    });
  }
});

// ─────────────────────────────────────────────
//  GET /history/:id — single decision detail
// ─────────────────────────────────────────────

router.get("/history/:id", async (req: Request, res: Response) => {
  const userId = (req as any).user?.userId;
  if (!userId) {
    return res.status(401).json({ error: "Authentication required" });
  }

  try {
    const decisionId = req.params.id as string;
    const decision = await getDecisionById(decisionId);
    if (!decision) {
      return res.status(404).json({ error: "Decision not found" });
    }
    if (decision.userId !== userId) {
      return res.status(403).json({ error: "Access denied" });
    }

    res.json({
      ...decision,
      createdAt: decision.createdAt?.toDate?.()
        ? decision.createdAt.toDate().toISOString()
        : decision.createdAt,
      updatedAt: decision.updatedAt?.toDate?.()
        ? decision.updatedAt.toDate().toISOString()
        : decision.updatedAt,
    });
  } catch (error: any) {
    logger.error("[Decision Engine] Failed to fetch decision", {
      decisionId: req.params.id as string,
      error: error.message,
    });
    res
      .status(500)
      .json({ error: "Failed to fetch decision", message: error.message });
  }
});

// ─────────────────────────────────────────────
//  POST /feedback/:id — submit execution feedback
// ─────────────────────────────────────────────

router.post("/feedback/:id", async (req: Request, res: Response) => {
  const userId = (req as any).user?.userId;
  if (!userId) {
    return res.status(401).json({ error: "Authentication required" });
  }

  const {
    actual_hardware_used,
    actual_execution_time_ms,
    actual_cost_usd,
    notes,
  } = req.body;

  // Validate required fields
  if (
    !actual_hardware_used ||
    actual_execution_time_ms === undefined ||
    actual_cost_usd === undefined
  ) {
    return res.status(400).json({
      error: "Missing required fields",
      required: [
        "actual_hardware_used",
        "actual_execution_time_ms",
        "actual_cost_usd",
      ],
    });
  }

  try {
    const feedback: FeedbackInput = {
      actual_hardware_used,
      actual_execution_time_ms: parseFloat(actual_execution_time_ms),
      actual_cost_usd: parseFloat(actual_cost_usd),
      notes: notes || undefined,
    };

    const decisionId = req.params.id as string;
    const success = await submitFeedback(decisionId, userId, feedback);

    if (!success) {
      return res
        .status(404)
        .json({ error: "Decision not found or access denied" });
    }

    res.json({ success: true, message: "Feedback submitted successfully" });
  } catch (error: any) {
    logger.error("[Decision Engine] Failed to submit feedback", {
      decisionId: req.params.id,
      error: error.message,
    });
    res
      .status(500)
      .json({ error: "Failed to submit feedback", message: error.message });
  }
});

// ─────────────────────────────────────────────
//  GET /accuracy — prediction accuracy stats
// ─────────────────────────────────────────────

router.get("/accuracy", async (req: Request, res: Response) => {
  const userId = (req as any).user?.userId;
  if (!userId) {
    return res.status(401).json({ error: "Authentication required" });
  }

  try {
    const stats = await getAccuracyStats(userId);
    res.json(stats);
  } catch (error: any) {
    logger.error("[Decision Engine] Failed to get accuracy stats", {
      userId,
      error: error.message,
    });
    res
      .status(500)
      .json({ error: "Failed to get accuracy stats", message: error.message });
  }
});

// ─────────────────────────────────────────────
//  GET /dashboard — aggregated dashboard stats
// ─────────────────────────────────────────────

router.get("/dashboard", async (req: Request, res: Response) => {
  const userId = (req as any).user?.userId;
  if (!userId) {
    return res.status(401).json({ error: "Authentication required" });
  }

  try {
    const stats = await getDashboardStats(userId);
    res.json(stats);
  } catch (error: any) {
    logger.error("[Decision Engine] Failed to get dashboard stats", {
      error: error.message,
    });
    res
      .status(500)
      .json({ error: "Failed to get dashboard stats", message: error.message });
  }
});

// ─────────────────────────────────────────────
//  Proxy routes (health, model-info)
// ─────────────────────────────────────────────

router.get("/health", forwardRequest);
router.get("/model-info", forwardRequest);

logger.debug("Decision Engine routes registered", {
  routes: [
    "POST /predict (with Firestore logging)",
    "GET /history",
    "GET /history/:id",
    "POST /feedback/:id",
    "GET /accuracy",
    "GET /dashboard",
    "GET /health",
    "GET /model-info",
  ],
});

export default router;
