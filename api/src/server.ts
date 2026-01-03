import express from 'express';
import type { Request, Response } from 'express';
import cors from 'cors';
import { logger } from '@config/logger.js';
import { corsOptions } from '@config/cors.js';
import decisionEngineRoutes from '@routes/decision-engine.js';
import hardwareRoutes from '@routes/hardware.js';

const app = express();
const PORT = process.env.PORT || 3000;
const DECISION_ENGINE_URL = process.env.DECISION_ENGINE_URL || 'http://localhost:8083';
const HARDWARE_LAYER_URL = process.env.HARDWARE_LAYER_URL || 'http://localhost:8084';

// CORS configuration
app.use(cors(corsOptions));

app.use(express.json());

// API Gateway routes for decision engine
app.use('/api/v1/decision-engine', decisionEngineRoutes);
// API Gateway routes for hardware layer
app.use('/api/v1/hardware', hardwareRoutes);

app.get('/', (req: Request, res: Response) => {
    res.json({ 
        message: 'Welcome to my modern TypeScript + Node.js API 🚀',
        endpoints: {
            decisionEngine: {
                base: '/api/v1/decision-engine',
                health: '/api/v1/decision-engine/health',
                predict: '/api/v1/decision-engine/predict'
            },
            hardware: {
                base: '/api/v1/hardware',
                status: '/api/v1/hardware/status'
            }
        }
    });
});

app.listen(PORT, () => {
    logger.info(`✅ Server running on http://localhost:${PORT}`);
    logger.info(`🔗 Decision Engine proxy: ${DECISION_ENGINE_URL}`);
    logger.info(`🔗 Hardware Layer proxy: ${HARDWARE_LAYER_URL}`);
});
