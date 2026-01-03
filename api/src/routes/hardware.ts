import { Router, type Request, type Response } from 'express';
import axios from 'axios';
import { logger } from '@config/logger.js';

const router = Router();
const HARDWARE_LAYER_URL = process.env.HARDWARE_LAYER_URL || 'http://localhost:8084';

// Handler function for forwarding requests to Hardware Layer
const forwardToHardware = async (req: Request, res: Response) => {
    try {
        const targetUrl = `${HARDWARE_LAYER_URL}/api/v1/hardware${req.path}`;
        
        logger.info(`[Hardware Gateway] ${req.method} ${req.originalUrl} -> ${targetUrl}`);

        const response = await axios({
            method: req.method,
            url: targetUrl,
            data: req.body,
            params: req.query,
            headers: {
                'Content-Type': req.headers['content-type'] || 'application/json',
            },
            timeout: 10000,
            validateStatus: () => true 
        });

        res.status(response.status).json(response.data);
    } catch (error: any) {
        logger.error('[Hardware Gateway Error]', { 
            error: error.message, 
            url: req.originalUrl 
        });

        res.status(503).json({
            error: 'Hardware Layer Service unavailable',
            message: error.message
        });
    }
};

// Define hardware routes
router.get('/status', forwardToHardware);
router.get('/devices', forwardToHardware);

export default router;
