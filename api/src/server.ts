import "dotenv/config";
import express from 'express';
import type { Request, Response } from 'express';
import cors from 'cors';
import { logger } from '@config/logger.js';
import { corsOptions } from '@config/cors.js';
import { requestLoggerMiddleware } from '@middleware/request-logger.js';
import { authMiddleware } from '@middleware/auth.js';
import authRoutes from '@routes/auth.js';
import decisionEngineRoutes from '@routes/decision-engine.js';
import aiCodeConverterRoutes from '@routes/ai-code-converter.js';
import codeAnalysisRoutes from "@routes/code-analysis.js";
import hardwareRoutes from '@routes/hardware.js';

const app = express();
const PORT = process.env.PORT || 3000;
const DECISION_ENGINE_URL = process.env.DECISION_ENGINE_URL || 'http://localhost:8003';
const AI_CODE_CONVERTER_URL = process.env.AI_CODE_CONVERTER_URL || 'http://localhost:8000';
const CODE_ANALYSIS_ENGINE_URL = process.env.CODE_ANALYSIS_ENGINE_URL || "http://localhost:8002";
const HARDWARE_LAYER_URL = process.env.HARDWARE_LAYER_URL || 'http://localhost:8004';

// ---------------------------------------------------------------------------
// Startup configuration logging
// ---------------------------------------------------------------------------
logger.info("Initializing API server", {
  port: PORT,
  nodeEnv: process.env.NODE_ENV || "development",
  nodeVersion: process.version,
});

logger.debug("Service URLs configured", {
  decisionEngine: DECISION_ENGINE_URL,
  aiCodeConverter: AI_CODE_CONVERTER_URL,
  codeAnalysisEngine: CODE_ANALYSIS_ENGINE_URL,
  hardwareLayer: HARDWARE_LAYER_URL,
});

logger.debug("CORS configuration", { corsOptions });

// ---------------------------------------------------------------------------
// Global middleware
// ---------------------------------------------------------------------------
logger.debug("Registering global middleware: CORS");
app.use(cors(corsOptions));

logger.debug("Registering global middleware: JSON body parser");
app.use(express.json());

logger.debug("Registering global middleware: request logger");
app.use(requestLoggerMiddleware);

// ---------------------------------------------------------------------------
// Route mounting
// ---------------------------------------------------------------------------

// Auth routes (public)
logger.info("Mounting route group: /api/v1/auth (public)");
app.use('/api/v1/auth', authRoutes);

// Protected API Gateway routes
logger.info("Mounting route group: /api/v1/decision-engine (protected)");
app.use("/api/v1/decision-engine", authMiddleware, decisionEngineRoutes);

logger.info("Mounting route group: /api/v1/code-analysis-engine (protected)");
app.use("/api/v1/code-analysis-engine", authMiddleware, codeAnalysisRoutes);

logger.info("Mounting route group: /api/v1/hardware (protected)");
app.use('/api/v1/hardware', authMiddleware, hardwareRoutes);

logger.info("Mounting route group: /api (ai-code-converter, protected)");
app.use('/api/v1/ai-code-converter', authMiddleware, aiCodeConverterRoutes);

// ---------------------------------------------------------------------------
// Root endpoint
// ---------------------------------------------------------------------------
app.get("/", (req: Request, res: Response) => {
  logger.debug("Root endpoint hit", { requestId: req.requestId });
  res.json({
    message: "Welcome to my modern TypeScript + Node.js API",
    endpoints: {
      auth: {
        register: "/api/v1/auth/register",
        login: "/api/v1/auth/login",
        google: "/api/v1/auth/google",
        verifyEmail: "/api/v1/auth/verify-email",
        resendVerification: "/api/v1/auth/resend-verification",
        me: "/api/v1/auth/me",
      },
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
    logger.info("Server started successfully", {
      port: PORT,
      environment: process.env.NODE_ENV || "development",
    });
    logger.info(`Decision Engine proxy target: ${DECISION_ENGINE_URL}`);
    logger.info(`AI Code Converter proxy target: ${AI_CODE_CONVERTER_URL}`);
    logger.info(`Code Analysis Engine proxy target: ${CODE_ANALYSIS_ENGINE_URL}`);
    logger.info(`Hardware Layer proxy target: ${HARDWARE_LAYER_URL}`);
    logger.debug("All route groups mounted, server is ready to accept connections");
});
