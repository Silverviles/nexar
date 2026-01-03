import { Router, type Request, type Response } from "express";
import axios from "axios";
import { logger } from "@config/logger.js";

const router = Router();
// Change this URL to your FastAPI backend
const AI_CODE_CONVERTER_URL =
  process.env.AI_CODE_CONVERTER_URL || "http://127.0.0.1:8000";

// Handler function for forwarding requests
const forwardRequest = async (req: Request, res: Response) => {
  try {
    const targetUrl = `${AI_CODE_CONVERTER_URL}/api${req.path}`;

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
      error: "AI Code Converter service unavailable",
      message: error.message,
    });
  }
};

// Define routes that match your FastAPI endpoints
router.post("/translate", forwardRequest);
router.post("/execute", forwardRequest);

export default router;
