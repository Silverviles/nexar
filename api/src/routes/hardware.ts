import { Router, type Request, type Response } from 'express';
import axios from 'axios';
import { logger } from '@config/logger.js';

const router = Router();
const HARDWARE_LAYER_URL = process.env.HARDWARE_LAYER_URL || 'http://localhost:8004';

// Timeout constants
const DEFAULT_TIMEOUT = 10_000;   // 10s for read-only queries
const EXECUTION_TIMEOUT = 60_000; // 60s for job submission (transpilation + queuing can be slow)

/**
 * Generic proxy helper that forwards a request to the HAL backend.
 *
 * @param halPath  - The target path on the HAL (e.g. "/api/quantum/ibm-quantum/devices")
 * @param timeout  - Axios timeout in ms
 */
const proxyToHal = (halPath: string, timeout = DEFAULT_TIMEOUT) =>
    async (req: Request, res: Response) => {
        try {
            const targetUrl = `${HARDWARE_LAYER_URL}${halPath}`;

            logger.info(`[Hardware Gateway] ${req.method} ${req.originalUrl} -> ${targetUrl}`);

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

            res.status(response.status).json(response.data);
        } catch (error: any) {
            logger.error('[Hardware Gateway Error]', {
                error: error.message,
                url: req.originalUrl,
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
        try {
            const halPath = buildPath(req);
            const targetUrl = `${HARDWARE_LAYER_URL}${halPath}`;

            logger.info(`[Hardware Gateway] ${req.method} ${req.originalUrl} -> ${targetUrl}`);

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

            res.status(response.status).json(response.data);
        } catch (error: any) {
            logger.error('[Hardware Gateway Error]', {
                error: error.message,
                url: req.originalUrl,
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

export default router;
