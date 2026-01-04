import { Router, type Request, type Response } from "express";
import axios from "axios";
import { logger } from "@config/logger.js";

const router = Router();
const CODE_ANALYSIS_ENGINE_URL =
  process.env.CODE_ANALYSIS_ENGINE_URL || "http://localhost:8002";

// Handler function for forwarding requests
const forwardRequest = async (req: Request, res: Response) => {
  try {
    const targetUrl = `${CODE_ANALYSIS_ENGINE_URL}/api/v1/code-analysis-engine${req.path}`;

    logger.info(`[Gateway] ${req.method} ${req.originalUrl} -> ${targetUrl}`);

    const response = await axios({
      method: req.method,
      url: targetUrl,
      data: req.body,
      params: req.query,
      headers: {
        "Content-Type": req.headers["content-type"] || "application/json",
      },
      timeout: 30000, // 30 second timeout
      validateStatus: () => true, // Accept all status codes
    });

    logger.info(
      `[Gateway] Response ${response.status} from ${req.originalUrl}`
    );

    // Forward the response
    res.status(response.status).json(response.data);
  } catch (error: any) {
    logger.error("[Gateway Error]", {
      error: error.message,
      url: req.originalUrl,
      method: req.method,
    });

    res.status(503).json({
      error: "Code Analysis Engine service unavailable",
      message: error.message,
    });
  }
};

// Define specific routes for Code Analysis Engine
router.post("/analyze", forwardRequest);
router.post("/detect-language", forwardRequest);
router.get("/supported-languages", forwardRequest);
router.get("/health", forwardRequest);

export default router;
