/**
 * Pipeline Types
 * Mirrors the API gateway pipeline response shape.
 */

import type { AnalysisResult } from "./codeAnalysis";
import type { DecisionEngineResponse, CodeAnalysisInput } from "./decision-engine.tp";

// ── Request ──

export interface PipelineRequest {
  code: string;
  problem_size_strategy?: "loc" | "ast_nodes" | "algorithm_hints";
  budget_limit_usd?: number;
  auto_execute?: boolean;
}

// ── Response ──

export type PipelineStatus = "completed" | "partial" | "failed";

export interface PipelineStepTiming {
  analysis_ms: number | null;
  decision_ms: number | null;
  total_ms: number;
}

export interface PipelineResponse {
  pipeline_id: string;
  status: PipelineStatus;
  analysis: AnalysisResult | null;
  decision: (DecisionEngineResponse & { decision_id?: string | null }) | null;
  mapped_input: CodeAnalysisInput | null;
  execution: null;
  timing: PipelineStepTiming;
  error?: string;
}

// ── Pipeline UI Stage ──

export type PipelineStage =
  | "idle"
  | "running"
  | "analyzing"
  | "deciding"
  | "complete"
  | "error";
