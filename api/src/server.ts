import express from 'express';
import type { Request, Response } from 'express';
import cors from 'cors';
import { logger } from '@config/logger.js';
import { corsOptions } from '@config/cors.js';
import decisionEngineRoutes from '@routes/decision-engine.js';
import aiCodeConverterRoutes from '@routes/ai-code-coverter.js';
const app = express();
const PORT = process.env.PORT || 3000;
const DECISION_ENGINE_URL = process.env.DECISION_ENGINE_URL || 'http://localhost:8083';
const AI_CODE_CONVERTER_URL = process.env.AI_CODE_CONVERTER_URL || 'http://localhost:8000';

// CORS configuration
app.use(cors(corsOptions));
app.use(express.json());

// API Gateway routes for decision engine
app.use('/api/v1/decision-engine', decisionEngineRoutes);
app.use('/', aiCodeConverterRoutes);

app.get('/', (req: Request, res: Response) => {
    res.json({ 
        message: 'Welcome to my modern TypeScript + Node.js API 🚀',
        endpoints: {
            decisionEngine: '/api/v1/decision-engine',
            health: '/api/v1/decision-engine/health',
            predict: '/api/v1/decision-engine/predict'
        }
    });
});

app.get('/', (req: Request, res: Response) => {
    res.json({ 
        message: 'Welcome to Quantum Code Converter API Gateway',
        endpoints: {
            aiCodeConverter: '/',
            translate: '/translate',
            execute: '/execute',
            translate3: '/translate3'
        }
    });
});

app.listen(PORT, () => {
    logger.info(`✅ Server running on http://localhost:${PORT}`);
    logger.info(`🔗 Decision Engine proxy: ${DECISION_ENGINE_URL}`);
    logger.info(`🔗 AI Code Converter backend: ${AI_CODE_CONVERTER_URL}`);
});
