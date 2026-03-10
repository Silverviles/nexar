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
  cyclomatic_complexity_max: number;
  cognitive_complexity: number;
  time_complexity: TimeComplexity;
  space_complexity: string;
  loop_count: number;
  conditional_count: number;
  function_count: number;
  max_nesting_depth: number;
  control_flow_nesting_depth: number;
  structural_nesting_depth: number;
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
  logical_circuit_volume: number | null;
  estimated_logical_runtime_ms: number | null;
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
  is_quantum: boolean;
  confidence_score: number;
  analysis_notes: string;
  detected_algorithms: string[];
  algorithm_detection_source: string | null;
  code_quality_metrics?: CodeQualityMetrics;
  optimization_suggestions?: OptimizationSuggestion[];
  ast_structure?: ASTNode;
  language_detection_method?: string;
}

export interface ASTNode {
  type: string;
  name?: string | null;
  line_number?: number | null;
  complexity_score?: number | null;
  children?: ASTNode[] | null;
  attributes?: Record<string, any> | null;
}

export interface OptimizationSuggestion {
  category: string;
  severity: "low" | "medium" | "high";
  description: string;
  expected_improvement: string;
  estimated_savings?: Record<string, any>;
}

export interface CodeQualityMetrics {
  overall_score: number;
  maintainability_score: number;
  performance_score: number;
  resource_efficiency_score: number;
  code_complexity_rating: "Low" | "Medium" | "High" | "Very High";
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

export interface LanguageDetectionResponse {
  language: SupportedLanguage | "unknown";
  confidence: number;
  is_supported: boolean;
  details: string;
  method: "ml" | "fallback" | "error";
}

export interface CodeSubmission {
  code: string;
  filename?: string;
  problem_size_strategy?: "loc" | "ast_nodes" | "algorithm_hints";
}

export type OptimizationPreference = "cost" | "performance" | "balanced";
