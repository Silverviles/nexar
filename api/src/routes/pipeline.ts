/**
 * Pipeline Routes
 *
 * Orchestrates the end-to-end flow:
 *   Code → Analysis → Decision → (future: Execution)
 *
 * This is the integration layer that chains the independent microservices
 * into a single coherent pipeline, handling enum mapping between them.
 */

import { Router, type Request, type Response } from "express";
import axios from "axios";
import crypto from "crypto";
import { logger } from "@config/logger.js";
import { mapAnalysisToDecisionInput } from "@/services/analysis-to-decision-mapper.js";
import {
  logDecision,
} from "@/services/decision-log-service.js";
import type {
  PipelineRequest,
  PipelineResponse,
  CodeAnalysisResult,
  DecisionEngineResult,
  DecisionEngineInput,
} from "@/types/pipeline.js";

const router = Router();

const CODE_ANALYSIS_ENGINE_URL =
  process.env.CODE_ANALYSIS_ENGINE_URL || "http://localhost:8002";
const DECISION_ENGINE_URL =
  process.env.DECISION_ENGINE_URL || "http://localhost:8003";

const ANALYSIS_TIMEOUT = 30_000;
const DECISION_TIMEOUT = 30_000;

logger.debug("Pipeline routes initialized", {
  codeAnalysisUrl: CODE_ANALYSIS_ENGINE_URL,
  decisionEngineUrl: DECISION_ENGINE_URL,
});

// ─────────────────────────────────────────────
//  POST /run — full pipeline orchestration
// ─────────────────────────────────────────────

router.post("/run", async (req: Request, res: Response) => {
  const requestId = req.requestId;
  const pipelineId = crypto.randomUUID();
  const userId = (req as any).user?.userId || "anonymous";
  const body = req.body as PipelineRequest;

  logger.info("[Pipeline] Starting pipeline run", {
    requestId,
    pipelineId,
    userId,
    codeLength: body.code?.length ?? 0,
    problemSizeStrategy: body.problem_size_strategy,
    budgetLimit: body.budget_limit_usd,
    autoExecute: body.auto_execute,
  });

  if (!body.code || typeof body.code !== "string" || body.code.trim() === "") {
    logger.warn("[Pipeline] Empty or missing code in request", {
      requestId,
      pipelineId,
    });
    return res.status(400).json({
      pipeline_id: pipelineId,
      status: "failed",
      analysis: null,
      decision: null,
      mapped_input: null,
      execution: null,
      timing: { analysis_ms: null, decision_ms: null, total_ms: 0 },
      error: "Code is required and must be a non-empty string",
    } satisfies PipelineResponse);
  }

  const pipelineStart = Date.now();
  let analysisResult: CodeAnalysisResult | null = null;
  let decisionResult: DecisionEngineResult | null = null;
  let mappedInput: DecisionEngineInput | null = null;
  let analysisDuration: number | null = null;
  let decisionDuration: number | null = null;

  // ── Step 1: Code Analysis ──

  try {
    const analysisStart = Date.now();
    const analysisUrl = `${CODE_ANALYSIS_ENGINE_URL}/api/v1/code-analysis-engine/analyze`;

    logger.info("[Pipeline] Step 1: Calling Code Analysis Engine", {
      requestId,
      pipelineId,
      url: analysisUrl,
    });

    const analysisPayload: Record<string, any> = { code: body.code };
    if (body.problem_size_strategy) {
      analysisPayload.problem_size_strategy = body.problem_size_strategy;
    }

    const analysisResponse = await axios.post(analysisUrl, analysisPayload, {
      headers: { "Content-Type": "application/json" },
      timeout: ANALYSIS_TIMEOUT,
    });

    analysisDuration = Date.now() - analysisStart;
    analysisResult = analysisResponse.data as CodeAnalysisResult;

    logger.info("[Pipeline] Step 1 complete: Code Analysis succeeded", {
      requestId,
      pipelineId,
      durationMs: analysisDuration,
      detectedLanguage: analysisResult.detected_language,
      problemType: analysisResult.problem_type,
      isQuantum: analysisResult.is_quantum,
    });
  } catch (error: any) {
    analysisDuration = Date.now() - (pipelineStart);
    const totalMs = Date.now() - pipelineStart;

    logger.error("[Pipeline] Step 1 failed: Code Analysis error", {
      requestId,
      pipelineId,
      errorCode: error.code,
      errorMessage: error.message,
      statusCode: error.response?.status,
    });

    return res.status(503).json({
      pipeline_id: pipelineId,
      status: "failed",
      analysis: null,
      decision: null,
      mapped_input: null,
      execution: null,
      timing: {
        analysis_ms: analysisDuration,
        decision_ms: null,
        total_ms: totalMs,
      },
      error: `Code Analysis failed: ${error.message}`,
    } satisfies PipelineResponse);
  }

  // ── Step 2: Map Analysis → Decision Input ──

  try {
    mappedInput = mapAnalysisToDecisionInput(analysisResult);

    logger.info("[Pipeline] Step 2: Mapped analysis to decision input", {
      requestId,
      pipelineId,
      originalProblemType: analysisResult.problem_type,
      mappedProblemType: mappedInput.problem_type,
      originalTimeComplexity: analysisResult.time_complexity,
      mappedTimeComplexity: mappedInput.time_complexity,
    });
  } catch (error: any) {
    const totalMs = Date.now() - pipelineStart;

    logger.error("[Pipeline] Step 2 failed: Mapping error", {
      requestId,
      pipelineId,
      errorMessage: error.message,
    });

    // Return partial result — analysis succeeded but mapping failed
    return res.status(200).json({
      pipeline_id: pipelineId,
      status: "partial",
      analysis: analysisResult,
      decision: null,
      mapped_input: null,
      execution: null,
      timing: {
        analysis_ms: analysisDuration,
        decision_ms: null,
        total_ms: totalMs,
      },
      error: `Mapping failed: ${error.message}`,
    } satisfies PipelineResponse);
  }

  // ── Step 3: Decision Engine ──

  try {
    const decisionStart = Date.now();
    const decisionUrl = `${DECISION_ENGINE_URL}/api/v1/decision-engine/predict`;
    const budgetParam = body.budget_limit_usd
      ? `?budget_limit_usd=${body.budget_limit_usd}`
      : "";

    logger.info("[Pipeline] Step 3: Calling Decision Engine", {
      requestId,
      pipelineId,
      url: decisionUrl,
      mappedInput,
    });

    const decisionResponse = await axios.post(
      `${decisionUrl}${budgetParam}`,
      mappedInput,
      {
        headers: { "Content-Type": "application/json" },
        timeout: DECISION_TIMEOUT,
      }
    );

    decisionDuration = Date.now() - decisionStart;
    decisionResult = decisionResponse.data as DecisionEngineResult;

    logger.info("[Pipeline] Step 3 complete: Decision Engine succeeded", {
      requestId,
      pipelineId,
      durationMs: decisionDuration,
      success: decisionResult.success,
      recommended:
        decisionResult.recommendation?.recommended_hardware ?? "none",
      confidence: decisionResult.recommendation?.confidence ?? 0,
    });

    // Log decision to Firestore (non-blocking, same as decision-engine route)
    if (decisionResult.success) {
      logDecision({
        userId,
        requestBody: mappedInput,
        responseBody: decisionResult,
        ...(body.budget_limit_usd !== undefined && {
          budgetLimitUsd: body.budget_limit_usd,
        }),
      }).catch((logError) => {
        logger.error("[Pipeline] Failed to log decision to Firestore", {
          requestId,
          pipelineId,
          error: logError.message,
        });
      });
    }
  } catch (error: any) {
    decisionDuration = Date.now() - pipelineStart - (analysisDuration ?? 0);
    const totalMs = Date.now() - pipelineStart;

    logger.error("[Pipeline] Step 3 failed: Decision Engine error", {
      requestId,
      pipelineId,
      errorCode: error.code,
      errorMessage: error.message,
      statusCode: error.response?.status,
    });

    // Return partial result — analysis succeeded but decision failed
    return res.status(200).json({
      pipeline_id: pipelineId,
      status: "partial",
      analysis: analysisResult,
      decision: null,
      mapped_input: mappedInput,
      execution: null,
      timing: {
        analysis_ms: analysisDuration,
        decision_ms: decisionDuration,
        total_ms: totalMs,
      },
      error: `Decision Engine failed: ${error.message}`,
    } satisfies PipelineResponse);
  }

  // ── Complete ──

  const totalMs = Date.now() - pipelineStart;

  logger.info("[Pipeline] Pipeline completed successfully", {
    requestId,
    pipelineId,
    totalMs,
    analysisDurationMs: analysisDuration,
    decisionDurationMs: decisionDuration,
  });

  return res.status(200).json({
    pipeline_id: pipelineId,
    status: "completed",
    analysis: analysisResult,
    decision: decisionResult,
    mapped_input: mappedInput,
    execution: null,
    timing: {
      analysis_ms: analysisDuration,
      decision_ms: decisionDuration,
      total_ms: totalMs,
    },
  } satisfies PipelineResponse);
});

// ─────────────────────────────────────────────
//  GET /health — pipeline health check
// ─────────────────────────────────────────────

router.get("/health", async (_req: Request, res: Response) => {
  const checks: Record<string, string> = {};

  // Check Code Analysis Engine
  try {
    await axios.get(
      `${CODE_ANALYSIS_ENGINE_URL}/api/v1/code-analysis-engine/health`,
      { timeout: 5000 }
    );
    checks.code_analysis = "healthy";
  } catch {
    checks.code_analysis = "unavailable";
  }

  // Check Decision Engine
  try {
    await axios.get(
      `${DECISION_ENGINE_URL}/api/v1/decision-engine/health`,
      { timeout: 5000 }
    );
    checks.decision_engine = "healthy";
  } catch {
    checks.decision_engine = "unavailable";
  }

  const allHealthy = Object.values(checks).every((s) => s === "healthy");

  res.status(allHealthy ? 200 : 503).json({
    status: allHealthy ? "healthy" : "degraded",
    services: checks,
  });
});

logger.debug("Pipeline routes registered", {
  routes: ["POST /run", "GET /health"],
});

export default router;
