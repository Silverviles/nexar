/**
 * TypeScript Types for Code Analysis Engine
 */

export type SupportedLanguage =
  | "python"
  | "qiskit"
  | "qsharp"
  | "cirq"
  | "openqasm";

export type ProblemType =
  | "search"
  | "optimization"
  | "simulation"
  | "machine_learning"
  | "factorization"
  | "cryptography"
  | "sampling"
  | "classical"
  | "unknown";

export type TimeComplexity =
  | "O(1)"
  | "O(log n)"
  | "O(n)"
  | "O(n log n)"
  | "O(n^2)"
  | "O(n^3)"
  | "O(2^n)"
  | "O(n!)"
  | "O(n^k)"
  | "O(sqrt(n))"
  | "unknown";

export interface ClassicalMetrics {
  cyclomatic_complexity: number;
  cognitive_complexity: number;
  time_complexity: TimeComplexity;
  space_complexity: string;
  loop_count: number;
  conditional_count: number;
  function_count: number;
  max_nesting_depth: number;
  lines_of_code: number;
}

export interface QuantumMetrics {
  qubits_required: number;
  circuit_depth: number;
  gate_count: number;
  single_qubit_gates: number;
  two_qubit_gates: number;
  cx_gate_count: number;
  cx_gate_ratio: number;
  measurement_count: number;
  superposition_score: number;
  entanglement_score: number;
  has_superposition: boolean;
  has_entanglement: boolean;
  quantum_volume: number | null;
  estimated_runtime_ms: number | null;
}

export interface AnalysisResult {
  detected_language: SupportedLanguage;
  language_confidence: number;
  problem_type: ProblemType;
  problem_size: number;
  classical_metrics: ClassicalMetrics | null;
  quantum_metrics: QuantumMetrics | null;
  qubits_required: number;
  circuit_depth: number;
  gate_count: number;
  cx_gate_ratio: number;
  superposition_score: number;
  entanglement_score: number;
  time_complexity: TimeComplexity;
  memory_requirement_mb: number;
  is_quantum_eligible: boolean;
  confidence_score: number;
  analysis_notes: string;
  detected_algorithms: string[];
  algorithm_detection_source: string | null;
}

export interface Language {
  name: string;
  value: SupportedLanguage;
  logo?: string;
}

export interface SupportedLanguagesResponse {
  languages: Language[];
  count: number;
}

export interface CodeSubmission {
  code: string;
  filename?: string;
}

export type OptimizationPreference = "cost" | "performance" | "balanced";
