import { Router, type Request, type Response } from 'express';
import axios from 'axios';
import { logger } from '@config/logger.js';

const router = Router();
const DECISION_ENGINE_URL = process.env.DECISION_ENGINE_URL || 'http://localhost:8003';
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
  if (error.code === 'ECONNREFUSED') {
    return { errorType: 'connection_refused', detail: 'Decision Engine service is not running or not reachable' };
  }
  if (error.code === 'ETIMEDOUT' || error.code === 'ECONNABORTED') {
    return { errorType: 'timeout', detail: `Request timed out after ${REQUEST_TIMEOUT}ms` };
  }
  if (error.code === 'ENOTFOUND') {
    return { errorType: 'dns_failure', detail: 'Could not resolve Decision Engine hostname' };
  }
  if (error.code === 'ECONNRESET') {
    return { errorType: 'connection_reset', detail: 'Connection was reset by the upstream service' };
  }
  return { errorType: 'network_error', detail: error.message || 'Unknown network error' };
}

// Handler function for forwarding requests
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
        contentType: req.headers['content-type'] || 'application/json',
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
                'Content-Type': req.headers['content-type'] || 'application/json',
            },
            timeout: REQUEST_TIMEOUT,
            validateStatus: () => true // Accept all status codes
        });

        const durationMs = Date.now() - startTime;
        const responseBodySize = response.data ? JSON.stringify(response.data).length : 0;

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
            responseContentType: response.headers['content-type'],
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

        logger.error('[Decision Engine] Upstream request failed', {
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
            error: 'Decision Engine service unavailable',
            message: error.message
        });
    }
};

// Define specific routes
router.post('/predict', forwardRequest);
router.get('/health', forwardRequest);
router.get('/model-info', forwardRequest);

logger.debug("Decision Engine routes registered", {
  routes: ["POST /predict", "GET /health", "GET /model-info"],
});

export default router;
