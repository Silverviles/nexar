
import api from '@/lib/axios';
import {
  ProblemType,
  TimeComplexity,
  type CodeAnalysisInput,
  type DecisionEngineResponse,
  type HealthCheckResponse
} from '@/types/decision-engine.tp';

const API_BASE = '/v1/decision-engine';

export const decisionEngineService = {
  /**
   * Get decision engine health status
   */
  async getHealth(): Promise<HealthCheckResponse> {
    const { data } = await api.get<HealthCheckResponse>(`${API_BASE}/health`);
    return data;
  },

  /**
   * Get hardware recommendation for given parameters
   */
  async predict(input: CodeAnalysisInput, budgetLimitUsd?: number): Promise<DecisionEngineResponse> {
    const params = budgetLimitUsd ? { budget_limit_usd: budgetLimitUsd } : {};
    const { data } = await api.post<DecisionEngineResponse>(`${API_BASE}/predict`, input, { params });
    return data;
  },

  /**
   * Get model information and metadata
   */
  async getModelInfo(): Promise<any> {
    const { data } = await api.get(`${API_BASE}/model-info`);
    return data;
  }
};

// Helper function to get problem type label
export const getProblemTypeLabel = (type: ProblemType): string => {
  const labels: Record<ProblemType, string> = {
    [ProblemType.FACTORIZATION]: 'Factorization',
    [ProblemType.SEARCH]: 'Search',
    [ProblemType.SIMULATION]: 'Simulation',
    [ProblemType.OPTIMIZATION]: 'Optimization',
    [ProblemType.SORTING]: 'Sorting',
    [ProblemType.DYNAMIC_PROGRAMMING]: 'Dynamic Programming',
    [ProblemType.MATRIX_OPS]: 'Matrix Operations',
    [ProblemType.RANDOM_CIRCUIT]: 'Random Circuit'
  };
  return labels[type];
};

// Helper function to get time complexity label
export const getTimeComplexityLabel = (complexity: TimeComplexity): string => {
  const labels: Record<TimeComplexity, string> = {
    [TimeComplexity.EXPONENTIAL]: 'Exponential',
    [TimeComplexity.POLYNOMIAL]: 'Polynomial',
    [TimeComplexity.QUADRATIC_SPEEDUP]: 'Quadratic Speedup',
    [TimeComplexity.POLYNOMIAL_SPEEDUP]: 'Polynomial Speedup',
    [TimeComplexity.NLOGN]: 'O(n log n)'
  };
  return labels[complexity];
};

// Field descriptions for the form
export const fieldDescriptions = {
  problem_type: 'The type of computational problem being solved',
  problem_size: 'Size of the problem (e.g., number of elements to process)',
  qubits_required: 'Number of qubits needed for quantum execution (0 for classical-only)',
  circuit_depth: 'Depth of the quantum circuit (0 for classical)',
  gate_count: 'Total number of quantum gates in the circuit (0 for classical)',
  cx_gate_ratio: 'Ratio of entangling gates (CNOT/CX gates) - value between 0 and 1',
  superposition_score: 'Potential to benefit from quantum superposition - value between 0 and 1',
  entanglement_score: 'Potential to benefit from quantum entanglement - value between 0 and 1',
  time_complexity: 'Algorithm time complexity class',
  memory_requirement_mb: 'Memory required to execute the algorithm in megabytes'
};