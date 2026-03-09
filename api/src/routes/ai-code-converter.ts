import { Router, type Request, type Response } from "express";
import axios from "axios";
import { logger } from "@config/logger.js";

const router = Router();
// Change this URL to your FastAPI backend
const AI_CODE_CONVERTER_URL =
  process.env.AI_CODE_CONVERTER_URL || "http://127.0.0.1:8000";
const DEFAULT_TIMEOUT = 30_000;       // 30s for lightweight endpoints
const MODEL_INFERENCE_TIMEOUT = 120_000; // 120s for T5 model inference (/translate)
const EXECUTION_TIMEOUT = 150_000;    // 150s for circuit execution (HAL polling can be slow)
const SLOW_UPSTREAM_THRESHOLD_MS = 100_000;

logger.debug("AI Code Converter routes initialized", {
  targetUrl: AI_CODE_CONVERTER_URL,
  defaultTimeoutMs: DEFAULT_TIMEOUT,
  modelInferenceTimeoutMs: MODEL_INFERENCE_TIMEOUT,
  executionTimeoutMs: EXECUTION_TIMEOUT,
});

/**
 * Categorize axios/network errors into actionable types.
 */
function categorizeError(error: any, timeout: number): { errorType: string; detail: string } {
  if (error.code === "ECONNREFUSED") {
    return { errorType: "connection_refused", detail: "AI Code Converter service is not running or not reachable" };
  }
  if (error.code === "ETIMEDOUT" || error.code === "ECONNABORTED") {
    return { errorType: "timeout", detail: `Request timed out after ${timeout}ms` };
  }
  if (error.code === "ENOTFOUND") {
    return { errorType: "dns_failure", detail: "Could not resolve AI Code Converter hostname" };
  }
  if (error.code === "ECONNRESET") {
    return { errorType: "connection_reset", detail: "Connection was reset by the upstream service" };
  }
  return { errorType: "network_error", detail: error.message || "Unknown network error" };
}

// Handler factory — returns a request forwarder with the given timeout
const createForwarder = (timeout: number) => async (req: Request, res: Response) => {
  const requestId = req.requestId;
  const targetUrl = `${AI_CODE_CONVERTER_URL}/api${req.path}`;

  logger.info("[AI Code Converter] Proxying request", {
    requestId,
    method: req.method,
    originalUrl: req.originalUrl,
    targetUrl,
  });

  logger.debug("[AI Code Converter] Upstream request details", {
    requestId,
    method: req.method,
    targetUrl,
    bodySize: req.body ? JSON.stringify(req.body).length : 0,
    contentType: req.headers["content-type"] || "application/json",
    queryParams: req.query,
    timeoutMs: timeout,
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
      timeout,
      validateStatus: () => true,
    });

    const durationMs = Date.now() - startTime;
    const responseBodySize = response.data ? JSON.stringify(response.data).length : 0;

    logger.info("[AI Code Converter] Upstream response received", {
      requestId,
      statusCode: response.status,
      durationMs,
      responseBodySize,
      originalUrl: req.originalUrl,
    });

    logger.debug("[AI Code Converter] Upstream response details", {
      requestId,
      statusCode: response.status,
      statusText: response.statusText,
      durationMs,
      responseBodySize,
      responseContentType: response.headers["content-type"],
    });

    // Warn on non-2xx upstream responses
    if (response.status >= 500) {
      logger.error("[AI Code Converter] Upstream returned server error", {
        requestId,
        statusCode: response.status,
        targetUrl,
        durationMs,
        responsePreview: JSON.stringify(response.data).substring(0, 500),
      });
    } else if (response.status >= 400) {
      logger.warn("[AI Code Converter] Upstream returned client error", {
        requestId,
        statusCode: response.status,
        targetUrl,
        durationMs,
        responsePreview: JSON.stringify(response.data).substring(0, 500),
      });
    }

    // Warn on slow responses
    if (durationMs > SLOW_UPSTREAM_THRESHOLD_MS) {
      logger.warn("[AI Code Converter] Slow upstream response", {
        requestId,
        durationMs,
        threshold: SLOW_UPSTREAM_THRESHOLD_MS,
        targetUrl,
      });
    }

    logger.debug("[AI Code Converter] Forwarding response to client", {
      requestId,
      statusCode: response.status,
    });

    // Forward the response
    res.status(response.status).json(response.data);
  } catch (error: any) {
    const durationMs = Date.now() - startTime;
    const { errorType, detail } = categorizeError(error, timeout);

    logger.error("[AI Code Converter] Upstream request failed", {
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
      error: "AI Code Converter service unavailable",
      message: error.message,
    });
  }
};

// Define routes that match your FastAPI endpoints
router.post("/translate", createForwarder(MODEL_INFERENCE_TIMEOUT));
router.post("/execute", createForwarder(EXECUTION_TIMEOUT));
router.post("/quantum/analyze", createForwarder(DEFAULT_TIMEOUT));
router.get("/devices", createForwarder(DEFAULT_TIMEOUT));

logger.debug("AI Code Converter routes registered", {
  routes: [
    "POST /translate", "POST /execute",
    "POST /quantum/analyze", "GET /devices",
  ],
});

export default router;
