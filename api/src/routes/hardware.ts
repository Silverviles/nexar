import { Router, type Request, type Response } from 'express';
import axios from 'axios';
import { logger } from '@config/logger.js';

const router = Router();
const HARDWARE_LAYER_URL = process.env.HARDWARE_LAYER_URL || 'http://localhost:8004';

// Timeout constants
const DEFAULT_TIMEOUT = 10_000;   // 10s for read-only queries
const EXECUTION_TIMEOUT = 60_000; // 60s for job submission (transpilation + queuing can be slow)
const SLOW_UPSTREAM_THRESHOLD_MS = 5_000;

logger.debug("Hardware routes initialized", {
    targetUrl: HARDWARE_LAYER_URL,
    defaultTimeoutMs: DEFAULT_TIMEOUT,
    executionTimeoutMs: EXECUTION_TIMEOUT,
});

/**
 * Categorize axios/network errors into actionable types.
 */
function categorizeError(error: any, timeout: number): { errorType: string; detail: string } {
    if (error.code === 'ECONNREFUSED') {
        return { errorType: 'connection_refused', detail: 'Hardware Abstraction Layer service is not running or not reachable' };
    }
    if (error.code === 'ETIMEDOUT' || error.code === 'ECONNABORTED') {
        return { errorType: 'timeout', detail: `Request timed out after ${timeout}ms` };
    }
    if (error.code === 'ENOTFOUND') {
        return { errorType: 'dns_failure', detail: 'Could not resolve Hardware Abstraction Layer hostname' };
    }
    if (error.code === 'ECONNRESET') {
        return { errorType: 'connection_reset', detail: 'Connection was reset by the upstream service' };
    }
    return { errorType: 'network_error', detail: error.message || 'Unknown network error' };
}

/**
 * Generic proxy helper that forwards a request to the HAL backend.
 *
 * @param halPath  - The target path on the HAL (e.g. "/api/quantum/ibm-quantum/devices")
 * @param timeout  - Axios timeout in ms
 */
const proxyToHal = (halPath: string, timeout = DEFAULT_TIMEOUT) =>
    async (req: Request, res: Response) => {
        const requestId = req.requestId;
        const targetUrl = `${HARDWARE_LAYER_URL}${halPath}`;

        logger.info(`[Hardware Gateway] Proxying request`, {
            requestId,
            method: req.method,
            originalUrl: req.originalUrl,
            targetUrl,
        });

        logger.debug("[Hardware Gateway] Upstream request details", {
            requestId,
            method: req.method,
            targetUrl,
            bodySize: req.body ? JSON.stringify(req.body).length : 0,
            contentType: req.headers['content-type'] || 'application/json',
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
                    'Content-Type': req.headers['content-type'] || 'application/json',
                },
                timeout,
                validateStatus: () => true,
            });

            const durationMs = Date.now() - startTime;
            const responseBodySize = response.data ? JSON.stringify(response.data).length : 0;

            logger.info("[Hardware Gateway] Upstream response received", {
                requestId,
                statusCode: response.status,
                durationMs,
                responseBodySize,
                originalUrl: req.originalUrl,
            });

            logger.debug("[Hardware Gateway] Upstream response details", {
                requestId,
                statusCode: response.status,
                statusText: response.statusText,
                durationMs,
                responseBodySize,
                responseContentType: response.headers['content-type'],
            });

            // Warn on non-2xx upstream responses
            if (response.status >= 500) {
                logger.error("[Hardware Gateway] Upstream returned server error", {
                    requestId,
                    statusCode: response.status,
                    targetUrl,
                    durationMs,
                    responsePreview: JSON.stringify(response.data).substring(0, 500),
                });
            } else if (response.status >= 400) {
                logger.warn("[Hardware Gateway] Upstream returned client error", {
                    requestId,
                    statusCode: response.status,
                    targetUrl,
                    durationMs,
                    responsePreview: JSON.stringify(response.data).substring(0, 500),
                });
            }

            // Warn on slow responses
            if (durationMs > SLOW_UPSTREAM_THRESHOLD_MS) {
                logger.warn("[Hardware Gateway] Slow upstream response", {
                    requestId,
                    durationMs,
                    threshold: SLOW_UPSTREAM_THRESHOLD_MS,
                    targetUrl,
                });
            }

            logger.debug("[Hardware Gateway] Forwarding response to client", {
                requestId,
                statusCode: response.status,
            });

            res.status(response.status).json(response.data);
        } catch (error: any) {
            const durationMs = Date.now() - startTime;
            const { errorType, detail } = categorizeError(error, timeout);

            logger.error('[Hardware Gateway] Upstream request failed', {
                requestId,
                errorType,
                detail,
                errorCode: error.code,
                errorMessage: error.message,
                targetUrl,
                method: req.method,
                originalUrl: req.originalUrl,
                durationMs,
            });

            res.status(503).json({
                error: 'Hardware Layer Service unavailable',
                message: error.message,
            });
        }
    };

/**
 * Parameterized proxy helper — builds the HAL path from Express route params.
 *
 * @param buildPath - Function that receives the Express Request and returns the HAL path
 * @param timeout   - Axios timeout in ms
 */
const proxyToHalDynamic = (buildPath: (req: Request) => string, timeout = DEFAULT_TIMEOUT) =>
    async (req: Request, res: Response) => {
        const requestId = req.requestId;
        const halPath = buildPath(req);
        const targetUrl = `${HARDWARE_LAYER_URL}${halPath}`;

        logger.info("[Hardware Gateway] Proxying dynamic request", {
            requestId,
            method: req.method,
            originalUrl: req.originalUrl,
            targetUrl,
            routeParams: req.params,
        });

        logger.debug("[Hardware Gateway] Dynamic upstream request details", {
            requestId,
            method: req.method,
            targetUrl,
            halPath,
            routeParams: req.params,
            bodySize: req.body ? JSON.stringify(req.body).length : 0,
            contentType: req.headers['content-type'] || 'application/json',
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
                    'Content-Type': req.headers['content-type'] || 'application/json',
                },
                timeout,
                validateStatus: () => true,
            });

            const durationMs = Date.now() - startTime;
            const responseBodySize = response.data ? JSON.stringify(response.data).length : 0;

            logger.info("[Hardware Gateway] Upstream response received", {
                requestId,
                statusCode: response.status,
                durationMs,
                responseBodySize,
                originalUrl: req.originalUrl,
            });

            logger.debug("[Hardware Gateway] Upstream response details", {
                requestId,
                statusCode: response.status,
                statusText: response.statusText,
                durationMs,
                responseBodySize,
                responseContentType: response.headers['content-type'],
                routeParams: req.params,
            });

            // Warn on non-2xx upstream responses
            if (response.status >= 500) {
                logger.error("[Hardware Gateway] Upstream returned server error", {
                    requestId,
                    statusCode: response.status,
                    targetUrl,
                    durationMs,
                    routeParams: req.params,
                    responsePreview: JSON.stringify(response.data).substring(0, 500),
                });
            } else if (response.status >= 400) {
                logger.warn("[Hardware Gateway] Upstream returned client error", {
                    requestId,
                    statusCode: response.status,
                    targetUrl,
                    durationMs,
                    routeParams: req.params,
                    responsePreview: JSON.stringify(response.data).substring(0, 500),
                });
            }

            // Warn on slow responses
            if (durationMs > SLOW_UPSTREAM_THRESHOLD_MS) {
                logger.warn("[Hardware Gateway] Slow upstream response", {
                    requestId,
                    durationMs,
                    threshold: SLOW_UPSTREAM_THRESHOLD_MS,
                    targetUrl,
                    routeParams: req.params,
                });
            }

            logger.debug("[Hardware Gateway] Forwarding response to client", {
                requestId,
                statusCode: response.status,
            });

            res.status(response.status).json(response.data);
        } catch (error: any) {
            const durationMs = Date.now() - startTime;
            const { errorType, detail } = categorizeError(error, timeout);

            logger.error('[Hardware Gateway] Dynamic upstream request failed', {
                requestId,
                errorType,
                detail,
                errorCode: error.code,
                errorMessage: error.message,
                targetUrl,
                halPath,
                method: req.method,
                originalUrl: req.originalUrl,
                routeParams: req.params,
                durationMs,
            });

            res.status(503).json({
                error: 'Hardware Layer Service unavailable',
                message: error.message,
            });
        }
    };


// =============================================================================
// Hardware Status & Discovery
// =============================================================================

// GET /api/v1/hardware/status  ->  HAL GET /api/v1/hardware/status
router.get('/status', proxyToHal('/api/v1/hardware/status'));

// GET /api/v1/hardware/devices  ->  HAL GET /api/v1/hardware/devices
router.get('/devices', proxyToHal('/api/v1/hardware/devices'));

// GET /api/v1/hardware/providers  ->  HAL GET /api/providers
router.get('/providers', proxyToHal('/api/providers'));

// GET /api/v1/hardware/quantum/:provider/devices  ->  HAL GET /api/quantum/:provider/devices
router.get(
    '/quantum/:provider/devices',
    proxyToHalDynamic((req) => `/api/quantum/${req.params.provider}/devices`),
);


// =============================================================================
// Quantum Execution
// =============================================================================

// POST /api/v1/hardware/quantum/:provider/execute  ->  HAL POST /api/quantum/:provider/execute
// Submits a QASM circuit for execution on the specified quantum provider & device.
router.post(
    '/quantum/:provider/execute',
    proxyToHalDynamic((req) => `/api/quantum/${req.params.provider}/execute`, EXECUTION_TIMEOUT),
);

// POST /api/v1/hardware/quantum/execute-python  ->  HAL POST /api/quantum/ibm-quantum/execute-python
// Submits raw Python code (must define a `circuit` variable) for IBM Quantum execution.
router.post(
    '/quantum/execute-python',
    proxyToHal('/api/quantum/ibm-quantum/execute-python', EXECUTION_TIMEOUT),
);


// =============================================================================
// Classical Execution
// =============================================================================

// POST /api/v1/hardware/classical/:provider/execute  ->  HAL POST /api/classical/:provider/execute
// Submits a classical compute task (Python code) to the specified classical provider.
router.post(
    '/classical/:provider/execute',
    proxyToHalDynamic((req) => `/api/classical/${req.params.provider}/execute`, EXECUTION_TIMEOUT),
);


// =============================================================================
// Job Scheduling (Quantum)
// =============================================================================

// POST /api/v1/hardware/quantum/schedule  ->  HAL POST /api/quantum/ibm-quantum/schedule
router.post(
    '/quantum/schedule',
    proxyToHal('/api/quantum/ibm-quantum/schedule', EXECUTION_TIMEOUT),
);

// GET /api/v1/hardware/quantum/scheduled-jobs  ->  HAL GET /api/quantum/ibm-quantum/scheduled-jobs
router.get(
    '/quantum/scheduled-jobs',
    proxyToHal('/api/quantum/ibm-quantum/scheduled-jobs'),
);

// DELETE /api/v1/hardware/quantum/scheduled-jobs/:jobId  ->  HAL DELETE /api/quantum/ibm-quantum/scheduled-jobs/:jobId
router.delete(
    '/quantum/scheduled-jobs/:jobId',
    proxyToHalDynamic((req) => `/api/quantum/ibm-quantum/scheduled-jobs/${req.params.jobId}`),
);


// =============================================================================
// Device Availability (Quantum)
// =============================================================================

// GET /api/v1/hardware/quantum/devices/:device/availability
//   -> HAL GET /api/quantum/ibm-quantum/devices/:device/availability
router.get(
    '/quantum/devices/:device/availability',
    proxyToHalDynamic((req) => `/api/quantum/ibm-quantum/devices/${req.params.device}/availability`),
);


// =============================================================================
// Job Status & Results (Generic — works for both quantum and classical jobs)
// =============================================================================

// GET /api/v1/hardware/jobs/:provider/:jobId  ->  HAL GET /api/jobs/:provider/:jobId
router.get(
    '/jobs/:provider/:jobId',
    proxyToHalDynamic((req) => `/api/jobs/${req.params.provider}/${req.params.jobId}`),
);

// GET /api/v1/hardware/jobs/:provider/:jobId/result  ->  HAL GET /api/jobs/:provider/:jobId/result
router.get(
    '/jobs/:provider/:jobId/result',
    proxyToHalDynamic((req) => `/api/jobs/${req.params.provider}/${req.params.jobId}/result`),
);


// =============================================================================
// Health Check
// =============================================================================

// GET /api/v1/hardware/health  ->  HAL GET /api/health
router.get('/health', proxyToHal('/api/health'));

logger.debug("Hardware routes registered", {
    routes: [
        "GET /status", "GET /devices", "GET /providers",
        "GET /quantum/:provider/devices",
        "POST /quantum/:provider/execute", "POST /quantum/execute-python",
        "POST /classical/:provider/execute",
        "POST /quantum/schedule", "GET /quantum/scheduled-jobs",
        "DELETE /quantum/scheduled-jobs/:jobId",
        "GET /quantum/devices/:device/availability",
        "GET /jobs/:provider/:jobId", "GET /jobs/:provider/:jobId/result",
        "GET /health",
    ],
});

export default router;
