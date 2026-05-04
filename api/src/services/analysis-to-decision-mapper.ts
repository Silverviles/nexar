/**
 * Analysis-to-Decision Mapper
 *
 * Maps CodeAnalysisResult (from code-analysis-engine) to DecisionEngineInput
 * (for decision-engine). These two services use different enum values for
 * ProblemType and TimeComplexity; this module bridges that gap.
 */

import type { CodeAnalysisResult, DecisionEngineInput } from "@/types/pipeline.js";

// ── ProblemType Mapping ──
// Code Analysis Engine → Decision Engine

const PROBLEM_TYPE_MAP: Record<string, string> = {
  search: "search",
  optimization: "optimization",
  simulation: "simulation",
  factorization: "factorization",
  machine_learning: "matrix_ops",
  cryptography: "factorization",
  sampling: "random_circuit",
  oracle_identification: "search",
  property_testing: "search",
  hidden_structure: "factorization",
  classical: "sorting",
  unknown: "optimization",
};

// ── TimeComplexity Mapping ──
// Code Analysis Engine → Decision Engine

const TIME_COMPLEXITY_MAP: Record<string, string> = {
  "O(1)": "polynomial",
  "O(log n)": "polynomial",
  "O(n)": "polynomial",
  "O(n log n)": "nlogn",
  "O(n^2)": "polynomial",
  "O(n^3)": "polynomial",
  "O(n^k)": "polynomial",
  "O(2^n)": "exponential",
  "O(n!)": "exponential",
  "O(sqrt(n))": "quadratic_speedup",
  unknown: "polynomial",
};

/**
 * Maps a CodeAnalysisResult to a DecisionEngineInput.
 *
 * Translates enum values and passes through numeric fields directly.
 * Falls back to safe defaults when an unmapped value is encountered.
 */
export function mapAnalysisToDecisionInput(
  analysis: CodeAnalysisResult
): DecisionEngineInput {
  const problemType =
    PROBLEM_TYPE_MAP[analysis.problem_type] ?? "optimization";

  const timeComplexity =
    TIME_COMPLEXITY_MAP[analysis.time_complexity] ?? "polynomial";

  return {
    problem_type: problemType,
    problem_size: analysis.problem_size,
    qubits_required: analysis.qubits_required,
    circuit_depth: analysis.circuit_depth,
    gate_count: analysis.gate_count,
    cx_gate_ratio: analysis.cx_gate_ratio,
    superposition_score: analysis.superposition_score,
    entanglement_score: analysis.entanglement_score,
    time_complexity: timeComplexity,
    memory_requirement_mb: analysis.memory_requirement_mb,
  };
}
