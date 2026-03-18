/**
 * Pipeline Types
 * Request/response interfaces for the unified pipeline orchestration endpoint.
 */

// ── Request ──

export interface PipelineRequest {
  code: string;
  problem_size_strategy?: "loc" | "ast_nodes" | "algorithm_hints";
  budget_limit_usd?: number;
  auto_execute?: boolean;
}

// ── Code Analysis types (mirrors code-analysis-engine output) ──

export interface CodeAnalysisResult {
  detected_language: string;
  language_confidence: number;
  problem_type: string;
  problem_size: number;
  classical_metrics: Record<string, any> | null;
  quantum_metrics: Record<string, any> | null;
  qubits_required: number;
  circuit_depth: number;
  gate_count: number;
  cx_gate_ratio: number;
  superposition_score: number;
  entanglement_score: number;
  time_complexity: string;
  memory_requirement_mb: number;
  is_quantum: boolean;
  confidence_score: number;
  analysis_notes: string;
  detected_algorithms: string[];
  algorithm_detection_source: string | null;
  code_quality_metrics?: Record<string, any>;
  optimization_suggestions?: Record<string, any>[];
  ast_structure?: Record<string, any>;
  language_detection_method?: string;
}

// ── Decision Engine types (mirrors decision-engine input/output) ──

export interface DecisionEngineInput {
  problem_type: string;
  problem_size: number;
  qubits_required: number;
  circuit_depth: number;
  gate_count: number;
  cx_gate_ratio: number;
  superposition_score: number;
  entanglement_score: number;
  time_complexity: string;
  memory_requirement_mb: number;
}

export interface DecisionEngineResult {
  success: boolean;
  recommendation: {
    recommended_hardware: string;
    confidence: number;
    quantum_probability: number;
    classical_probability: number;
    rationale: string;
  } | null;
  alternatives: Array<{
    hardware: string;
    confidence: number;
    trade_off: string;
  }> | null;
  estimated_execution_time_ms: number | null;
  estimated_cost_usd: number | null;
  error: string | null;
  decision_id?: string | null;
}

// ── Pipeline Response ──

export type PipelineStatus = "completed" | "partial" | "failed";

export interface PipelineStepTiming {
  analysis_ms: number | null;
  decision_ms: number | null;
  total_ms: number;
}

export interface PipelineResponse {
  pipeline_id: string;
  status: PipelineStatus;
  analysis: CodeAnalysisResult | null;
  decision: DecisionEngineResult | null;
  mapped_input: DecisionEngineInput | null;
  execution: null; // Reserved for future execution integration
  timing: PipelineStepTiming;
  error?: string;
}
