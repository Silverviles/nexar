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
