/**
 * Pipeline Types
 * Mirrors the Firestore pipeline_jobs document shape.
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

// ── Response (from GET /status/:pipelineId) ──

export type PipelineStatus =
  | "processing"
  | "analyzing"
  | "deciding"
  | "completed"
  | "partial"
  | "failed";

export interface PipelineStepTiming {
  analysis_ms: number | null;
  decision_ms: number | null;
  total_ms: number | null;
}

export interface PipelineResponse {
  pipeline_id: string;
  user_id?: string;
  status: PipelineStatus;
  analysis: AnalysisResult | null;
  decision: (DecisionEngineResponse & { decision_id?: string | null }) | null;
  mapped_input: CodeAnalysisInput | null;
  error?: string | null;
  timing: PipelineStepTiming;
  created_at?: string;
  updated_at?: string;
}

// ── Pipeline UI Stage (maps from PipelineStatus) ──

export type PipelineStage =
  | "idle"
  | "processing"
  | "analyzing"
  | "deciding"
  | "complete"
  | "error";
