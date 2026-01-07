// Decision Engine Types

export enum ProblemType {
  FACTORIZATION = 'factorization', // RW Ex: RSA encryption cracking
  SEARCH = 'search', // RW Ex: 
  SIMULATION = 'simulation', // RW Ex: Drug molecule analysis
  OPTIMIZATION = 'optimization', // RW Ex: Supply chain logistics
  SORTING = 'sorting', // RW Ex: Organizing customer data
  DYNAMIC_PROGRAMMING = 'dynamic_programming', // RW Ex: Fibonacci sequence
  MATRIX_OPS = 'matrix_ops', // RW Ex: Image processing
  RANDOM_CIRCUIT = 'random_circuit' // RW Ex:
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
  problem_type: ProblemType; //The category/type of computational problem you're trying to solve
  problem_size: number; // The scale/magnitude of your problem (problem-specific units)
  qubits_required: number; // How many quantum bits (qubits) you need to solve this problem
  circuit_depth: number; // How many sequential layers of quantum operations (gates) your circuit has
  gate_count: number; // Total number of quantum operations in your circuit
  cx_gate_ratio: number; // Percentage of gates that are CNOT (CX) gates - the most important quantum operation
  superposition_score: number; // How much your algorithm uses quantum superposition (being in multiple states simultaneously)
  entanglement_score: number; // How much your algorithm uses quantum entanglement (qubits affecting each other)
  time_complexity: TimeComplexity; // How the algorithm's runtime scales with problem size (Big O notation)
  memory_requirement_mb: number; // How much RAM/memory needed to solve the problem (in megabytes)
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
