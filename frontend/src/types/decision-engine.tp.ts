// Decision Engine Types

export enum ProblemType {
  FACTORIZATION = 'factorization',
  SEARCH = 'search',
  SIMULATION = 'simulation',
  OPTIMIZATION = 'optimization',
  SORTING = 'sorting',
  DYNAMIC_PROGRAMMING = 'dynamic_programming',
  MATRIX_OPS = 'matrix_ops',
  RANDOM_CIRCUIT = 'random_circuit'
}

export enum TimeComplexity {
  EXPONENTIAL = 'exponential',
  POLYNOMIAL = 'polynomial',
  QUADRATIC_SPEEDUP = 'quadratic_speedup',
  POLYNOMIAL_SPEEDUP = 'polynomial_speedup',
  NLOGN = 'nlogn'
}

export enum HardwareType {
  QUANTUM = 'Quantum',
  CLASSICAL = 'Classical',
  HYBRID = 'Hybrid'
}

export interface CodeAnalysisInput {
  problem_type: ProblemType;
  problem_size: number;
  qubits_required: number;
  circuit_depth: number;
  gate_count: number;
  cx_gate_ratio: number;
  superposition_score: number;
  entanglement_score: number;
  time_complexity: TimeComplexity;
  memory_requirement_mb: number;
}

export interface HardwareRecommendation {
  recommended_hardware: HardwareType;
  confidence: number;
  quantum_probability: number;
  classical_probability: number;
  rationale: string;
}

export interface Alternative {
  hardware: string;
  confidence: number;
  trade_off: string;
}

export interface DecisionEngineResponse {
  success: boolean;
  recommendation: HardwareRecommendation | null;
  alternatives: Alternative[] | null;
  estimated_execution_time_ms: number | null;
  estimated_cost_usd: number | null;
  error: string | null;
}

export interface HealthCheckResponse {
  status: string;
  model_loaded: boolean;
  model_type: string | null;
  model_accuracy: number | null;
}
