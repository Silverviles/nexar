export interface ConversionResult {
  metadata: {
    timestamp: string;
    shots: number;
    gateType: string;
  };
  pythonCode: string;
  quantumCode: string;
  executionResults: {
    success: boolean;
    used_generated_code: boolean;
    fallback_reason?: string;
    counts: Record<string, number>;
    probabilities: Record<string, number>;
    performance: {
      depth: number;
      num_qubits: number;
      num_gates: number;
      gate_counts: Record<string, number>;
      execution_time_seconds: number;
    };
    images?: {
      circuit_diagram: string;
      measurement_histogram: string;
    };
  };
  pythonPerformance?: {
    estimatedOpsPerSecond: number;
    estimatedPerOp: number;
    speedDifference: number;
  };
}

export interface PatternInfo {
  pattern: string;
  confidence: number;
  quantum_algo: string;
  speedup: string;
  suitability_score: number;
}

export interface QuantumSuitability {
  score: number;
  level: "high" | "medium" | "low";
  message: string;
}

export interface CodeMetrics {
  has_function: boolean;
  has_loop: boolean;
  has_condition: boolean;
  line_count: number;
  function_count: number;
  loop_count: number;
  condition_count: number;
}

export interface AnalysisResponse {
  success: boolean;
  patterns: PatternInfo[];
  quantum_suitability: QuantumSuitability;
  metrics: CodeMetrics;
  original_code?: string;
  error?: string;
}