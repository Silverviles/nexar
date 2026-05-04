/**
 * Client-side Analysis → Decision mapper
 *
 * Maps CodeAnalysisResult types to DecisionEngine input types.
 * This mirrors the server-side mapper in api/src/services/analysis-to-decision-mapper.ts
 * and is used for client-side transformations (e.g. displaying mapped values).
 */

import type { AnalysisResult, ProblemType as AnalysisProblemType, TimeComplexity as AnalysisTimeComplexity } from "@/types/codeAnalysis";
import { ProblemType, TimeComplexity, type CodeAnalysisInput } from "@/types/decision-engine.tp";

// ── ProblemType Mapping ──

const PROBLEM_TYPE_MAP: Record<AnalysisProblemType, ProblemType> = {
  search: ProblemType.SEARCH,
  optimization: ProblemType.OPTIMIZATION,
  simulation: ProblemType.SIMULATION,
  factorization: ProblemType.FACTORIZATION,
  machine_learning: ProblemType.MATRIX_OPS,
  cryptography: ProblemType.FACTORIZATION,
  sampling: ProblemType.RANDOM_CIRCUIT,
  classical: ProblemType.SORTING,
  unknown: ProblemType.OPTIMIZATION,
};

// ── TimeComplexity Mapping ──

const TIME_COMPLEXITY_MAP: Record<AnalysisTimeComplexity, TimeComplexity> = {
  "O(1)": TimeComplexity.POLYNOMIAL,
  "O(log n)": TimeComplexity.POLYNOMIAL,
  "O(n)": TimeComplexity.POLYNOMIAL,
  "O(n log n)": TimeComplexity.NLOGN,
  "O(n^2)": TimeComplexity.POLYNOMIAL,
  "O(n^3)": TimeComplexity.POLYNOMIAL,
  "O(n^k)": TimeComplexity.POLYNOMIAL,
  "O(2^n)": TimeComplexity.EXPONENTIAL,
  "O(n!)": TimeComplexity.EXPONENTIAL,
  "O(sqrt(n))": TimeComplexity.QUADRATIC_SPEEDUP,
  unknown: TimeComplexity.POLYNOMIAL,
};

/**
 * Maps an AnalysisResult to a CodeAnalysisInput for the Decision Engine.
 */
export function mapAnalysisToDecisionInput(
  analysis: AnalysisResult
): CodeAnalysisInput {
  return {
    problem_type: PROBLEM_TYPE_MAP[analysis.problem_type] ?? ProblemType.OPTIMIZATION,
    problem_size: analysis.problem_size,
    qubits_required: analysis.qubits_required,
    circuit_depth: analysis.circuit_depth,
    gate_count: analysis.gate_count,
    cx_gate_ratio: analysis.cx_gate_ratio,
    superposition_score: analysis.superposition_score,
    entanglement_score: analysis.entanglement_score,
    time_complexity: TIME_COMPLEXITY_MAP[analysis.time_complexity] ?? TimeComplexity.POLYNOMIAL,
    memory_requirement_mb: analysis.memory_requirement_mb,
  };
}
