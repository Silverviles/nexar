/**
 * Pipeline Routes
 *
 * Async orchestration: Code → Analysis → Decision
 *
 * POST /run    — accepts code, stores job in Firestore, returns 202 immediately,
 *                runs analysis + decision in the background.
 * GET /status/:id — polls Firestore for current pipeline job status + results.
 * GET /health  — checks downstream service health.
 */

import { Router, type Request, type Response } from "express";
import axios from "axios";
import crypto from "crypto";
import { logger } from "@config/logger.js";
import { mapAnalysisToDecisionInput } from "@/services/analysis-to-decision-mapper.js";
import { logDecision } from "@/services/decision-log-service.js";
import {
  createPipelineJob,
  updatePipelineJob,
  getPipelineJob,
} from "@/services/pipeline-job-service.js";
import type {
  PipelineRequest,
  CodeAnalysisResult,
  DecisionEngineResult,
  DecisionEngineInput,
} from "@/types/pipeline.js";

const router = Router();

const CODE_ANALYSIS_ENGINE_URL =
  process.env.CODE_ANALYSIS_ENGINE_URL || "http://localhost:8002";
const DECISION_ENGINE_URL =
  process.env.DECISION_ENGINE_URL || "http://localhost:8003";

const ANALYSIS_TIMEOUT = 300_000; // 5 min — large circuits (100+ qubits)
const DECISION_TIMEOUT = 30_000;

logger.debug("Pipeline routes initialized", {
  codeAnalysisUrl: CODE_ANALYSIS_ENGINE_URL,
  decisionEngineUrl: DECISION_ENGINE_URL,
});

// ─────────────────────────────────────────────
//  POST /run — async pipeline (returns 202)
// ─────────────────────────────────────────────

router.post("/run", async (req: Request, res: Response) => {
  const requestId = req.requestId;
  const pipelineId = crypto.randomUUID();
  const userId = (req as any).user?.userId || "anonymous";
  const body = req.body as PipelineRequest;

  logger.info("[Pipeline] Starting async pipeline run", {
    requestId,
    pipelineId,
    userId,
    codeLength: body.code?.length ?? 0,
  });

  if (!body.code || typeof body.code !== "string" || body.code.trim() === "") {
    return res.status(400).json({
      pipeline_id: pipelineId,
      status: "failed",
      error: "Code is required and must be a non-empty string",
    });
  }

  // Write initial job to Firestore and return immediately
  try {
    await createPipelineJob(pipelineId, userId, body.code);
  } catch (err: any) {
    logger.error("[Pipeline] Failed to create Firestore job", {
      requestId,
      pipelineId,
      error: err.message,
    });
    return res.status(500).json({
      pipeline_id: pipelineId,
      status: "failed",
      error: "Failed to initialize pipeline job",
    });
  }

  // Return 202 Accepted immediately
  res.status(202).json({
    pipeline_id: pipelineId,
    status: "processing",
  });

  // Run the pipeline in the background (non-blocking)
  runPipelineAsync(pipelineId, body, userId, requestId ?? pipelineId).catch((err) => {
    logger.error("[Pipeline] Unhandled error in background pipeline", {
      pipelineId,
      error: err.message,
    });
  });
});

// ─────────────────────────────────────────────
//  GET /status/:pipelineId — poll for results
// ─────────────────────────────────────────────

router.get("/status/:pipelineId", async (req: Request, res: Response) => {
  const userId = (req as any).user?.userId;
  const pipelineId = req.params.pipelineId as string;

  try {
    const job = await getPipelineJob(pipelineId);

    if (!job) {
      return res.status(404).json({ error: "Pipeline job not found" });
    }

    // Verify ownership
    if (job.user_id !== userId && userId !== "anonymous") {
      return res.status(403).json({ error: "Access denied" });
    }

    // Don't send the full code back in status polls (save bandwidth)
    const { code, ...jobWithoutCode } = job;

    return res.json(jobWithoutCode);
  } catch (err: any) {
    logger.error("[Pipeline] Failed to fetch job status", {
      pipelineId,
      error: err.message,
    });
    return res.status(500).json({ error: "Failed to fetch pipeline status" });
  }
});

// ─────────────────────────────────────────────
//  Background pipeline worker
// ─────────────────────────────────────────────

async function runPipelineAsync(
  pipelineId: string,
  body: PipelineRequest,
  userId: string,
  requestId: string
): Promise<void> {
  const pipelineStart = Date.now();

  let analysisResult: CodeAnalysisResult | null = null;
  let decisionResult: DecisionEngineResult | null = null;
  let mappedInput: DecisionEngineInput | null = null;
  let analysisDuration: number | null = null;
  let decisionDuration: number | null = null;

  // ── Step 1: Code Analysis ──

  try {
    await updatePipelineJob(pipelineId, { status: "analyzing" });

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
      isQuantum: analysisResult.is_quantum,
    });

    // Persist analysis results
    await updatePipelineJob(pipelineId, {
      analysis: analysisResult,
      timing: { analysis_ms: analysisDuration, decision_ms: null, total_ms: null },
    });
  } catch (error: any) {
    analysisDuration = Date.now() - pipelineStart;

    logger.error("[Pipeline] Step 1 failed: Code Analysis error", {
      requestId,
      pipelineId,
      errorCode: error.code,
      errorMessage: error.message,
    });

    await updatePipelineJob(pipelineId, {
      status: "failed",
      error: `Code Analysis failed: ${error.message}`,
      timing: { analysis_ms: analysisDuration, decision_ms: null, total_ms: Date.now() - pipelineStart },
    });
    return;
  }

  // ── Step 2: Map Analysis → Decision Input ──

  try {
    mappedInput = mapAnalysisToDecisionInput(analysisResult);

    logger.info("[Pipeline] Step 2: Mapped analysis to decision input", {
      requestId,
      pipelineId,
      originalProblemType: analysisResult.problem_type,
      mappedProblemType: mappedInput.problem_type,
    });
  } catch (error: any) {
    logger.error("[Pipeline] Step 2 failed: Mapping error", {
      requestId,
      pipelineId,
      errorMessage: error.message,
    });

    await updatePipelineJob(pipelineId, {
      status: "failed",
      mapped_input: null,
      error: `Mapping failed: ${error.message}`,
      timing: { analysis_ms: analysisDuration, decision_ms: null, total_ms: Date.now() - pipelineStart },
    });
    return;
  }

  // ── Step 3: Decision Engine ──

  try {
    await updatePipelineJob(pipelineId, {
      status: "deciding",
      mapped_input: mappedInput,
    });

    const decisionStart = Date.now();
    const decisionUrl = `${DECISION_ENGINE_URL}/api/v1/decision-engine/predict`;
    const budgetParam = body.budget_limit_usd
      ? `?budget_limit_usd=${body.budget_limit_usd}`
      : "";

    logger.info("[Pipeline] Step 3: Calling Decision Engine", {
      requestId,
      pipelineId,
      url: decisionUrl,
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
      recommended: decisionResult.recommendation?.recommended_hardware ?? "none",
    });

    // Log decision to Firestore (non-blocking)
    if (decisionResult.success) {
      logDecision({
        userId,
        requestBody: mappedInput,
        responseBody: decisionResult,
        ...(body.budget_limit_usd !== undefined && {
          budgetLimitUsd: body.budget_limit_usd,
        }),
      }).catch((logError) => {
        logger.error("[Pipeline] Failed to log decision", {
          pipelineId,
          error: logError.message,
        });
      });
    }
  } catch (error: any) {
    decisionDuration = Date.now() - pipelineStart - (analysisDuration ?? 0);

    logger.error("[Pipeline] Step 3 failed: Decision Engine error", {
      requestId,
      pipelineId,
      errorCode: error.code,
      errorMessage: error.message,
    });

    await updatePipelineJob(pipelineId, {
      status: "failed",
      decision: null,
      error: `Decision Engine failed: ${error.message}`,
      timing: {
        analysis_ms: analysisDuration,
        decision_ms: decisionDuration,
        total_ms: Date.now() - pipelineStart,
      },
    });
    return;
  }

  // ── Complete ──

  const totalMs = Date.now() - pipelineStart;

  logger.info("[Pipeline] Pipeline completed successfully", {
    requestId,
    pipelineId,
    totalMs,
  });

  await updatePipelineJob(pipelineId, {
    status: "completed",
    decision: decisionResult,
    timing: {
      analysis_ms: analysisDuration,
      decision_ms: decisionDuration,
      total_ms: totalMs,
    },
  });
}

// ─────────────────────────────────────────────
//  GET /health — pipeline health check
// ─────────────────────────────────────────────

router.get("/health", async (_req: Request, res: Response) => {
  const checks: Record<string, string> = {};

  try {
    await axios.get(
      `${CODE_ANALYSIS_ENGINE_URL}/api/v1/code-analysis-engine/health`,
      { timeout: 5000 }
    );
    checks.code_analysis = "healthy";
  } catch {
    checks.code_analysis = "unavailable";
  }

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
  routes: ["POST /run (async)", "GET /status/:pipelineId", "GET /health"],
});

export default router;
