import express from 'express';
import type { Request, Response } from 'express';
import cors from 'cors';
import { logger } from '@config/logger.js';
import { corsOptions } from '@config/cors.js';
import decisionEngineRoutes from '@routes/decision-engine.js';
import aiCodeConverterRoutes from '@routes/ai-code-converter.js';
import codeAnalysisRoutes from "@routes/code-analysis.js";
import dotenv from "dotenv";
dotenv.config();
import hardwareRoutes from '@routes/hardware.js';

const app = express();
const PORT = process.env.PORT || 3000;
const DECISION_ENGINE_URL = process.env.DECISION_ENGINE_URL || 'http://localhost:8003';
const AI_CODE_CONVERTER_URL = process.env.AI_CODE_CONVERTER_URL || 'http://localhost:8000';
const CODE_ANALYSIS_ENGINE_URL = process.env.CODE_ANALYSIS_ENGINE_URL || "http://localhost:8002";
const HARDWARE_LAYER_URL = process.env.HARDWARE_LAYER_URL || 'http://localhost:8004';

// CORS configuration
app.use(cors(corsOptions));
app.use(express.json());

// API Gateway routes for decision engine
app.use("/api/v1/decision-engine", decisionEngineRoutes);
app.use("/api/v1/code-analysis-engine", codeAnalysisRoutes);
app.use('/api/v1/hardware', hardwareRoutes);


// API Gateway routes for AI code converter
app.use('/api', aiCodeConverterRoutes);

app.get("/", (req: Request, res: Response) => {
  res.json({
    message: "Welcome to my modern TypeScript + Node.js API 🚀",
    endpoints: {
      decisionEngine: "/api/v1/decision-engine",
      health: "/api/v1/decision-engine/health",
      predict: "/api/v1/decision-engine/predict",
      codeAnalysis: "/api/v1/code-analysis-engine",
      codeAnalysishealth: "/api/v1/code-analysis-engine/health",
      analyze: "/api/v1/code-analysis-engine/analyze",
      detectLanguage: "/api/v1/code-analysis-engine/detect-language",
      supportedLanguages: "/api/v1/code-analysis-engine/supported-languages",
        hardware: {
            base: '/api/v1/hardware',
            status: '/api/v1/hardware/status',
            devices: '/api/v1/hardware/devices',
            providers: '/api/v1/hardware/providers',
            health: '/api/v1/hardware/health',
            quantumExecute: '/api/v1/hardware/quantum/:provider/execute',
            quantumExecutePython: '/api/v1/hardware/quantum/execute-python',
            classicalExecute: '/api/v1/hardware/classical/:provider/execute',
            quantumSchedule: '/api/v1/hardware/quantum/schedule',
            scheduledJobs: '/api/v1/hardware/quantum/scheduled-jobs',
            deviceAvailability: '/api/v1/hardware/quantum/devices/:device/availability',
            jobStatus: '/api/v1/hardware/jobs/:provider/:jobId',
            jobResult: '/api/v1/hardware/jobs/:provider/:jobId/result',
        }
    },
  });
});


app.listen(PORT, () => {
    logger.info(`✅ Server running on http://localhost:${PORT}`);
    logger.info(`🔗 Decision Engine proxy: ${DECISION_ENGINE_URL}`);
    logger.info(`🔗 AI Code Converter backend: ${AI_CODE_CONVERTER_URL}`);
    logger.info(`🔗 Code Analysis Engine proxy: ${CODE_ANALYSIS_ENGINE_URL}`);
    logger.info(`🔗 Hardware Layer proxy: ${HARDWARE_LAYER_URL}`);
});
