import { Router, type Request, type Response } from 'express';
import axios from 'axios';
import { logger } from '@config/logger.js';

const router = Router();
const DECISION_ENGINE_URL = process.env.DECISION_ENGINE_URL || 'http://localhost:8083';

// Handler function for forwarding requests
const forwardRequest = async (req: Request, res: Response) => {
    try {
        const targetUrl = `${DECISION_ENGINE_URL}/api/v1/decision-engine${req.path}`;
        
        logger.info(`[Gateway] ${req.method} ${req.originalUrl} -> ${targetUrl}`);

        const response = await axios({
            method: req.method,
            url: targetUrl,
            data: req.body,
            params: req.query,
            headers: {
                'Content-Type': req.headers['content-type'] || 'application/json',
            },
            timeout: 30000, // 30 second timeout
            validateStatus: () => true // Accept all status codes
        });

        logger.info(`[Gateway] Response ${response.status} from ${req.originalUrl}`);

        // Forward the response
        res.status(response.status).json(response.data);
    } catch (error: any) {
        logger.error('[Gateway Error]', { 
            error: error.message, 
            url: req.originalUrl,
            method: req.method
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

export default router;
