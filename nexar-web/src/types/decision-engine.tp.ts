// Decision Engine Types
// erasableSyntaxOnly forbids TS enums, so these use the const-object + union-type
// pattern instead -- ProblemType.FACTORIZATION dot-access still works identically.

export const ProblemType = {
  FACTORIZATION: 'factorization', // RW Ex: RSA encryption cracking
  SEARCH: 'search',
  SIMULATION: 'simulation', // RW Ex: Drug molecule analysis
  OPTIMIZATION: 'optimization', // RW Ex: Supply chain logistics
  SORTING: 'sorting', // RW Ex: Organizing customer data
  DYNAMIC_PROGRAMMING: 'dynamic_programming', // RW Ex: Fibonacci sequence
  MATRIX_OPS: 'matrix_ops', // RW Ex: Image processing
  RANDOM_CIRCUIT: 'random_circuit',
} as const
export type ProblemType = (typeof ProblemType)[keyof typeof ProblemType]

export const TimeComplexity = {
  EXPONENTIAL: 'exponential',
  POLYNOMIAL: 'polynomial',
  QUADRATIC_SPEEDUP: 'quadratic_speedup',
  POLYNOMIAL_SPEEDUP: 'polynomial_speedup',
  NLOGN: 'nlogn',
} as const
export type TimeComplexity = (typeof TimeComplexity)[keyof typeof TimeComplexity]

export const HardwareType = {
  QUANTUM: 'Quantum',
  CLASSICAL: 'Classical',
  HYBRID: 'Hybrid',
} as const
export type HardwareType = (typeof HardwareType)[keyof typeof HardwareType]

export interface CodeAnalysisInput {
  problem_type: ProblemType
  problem_size: number
  qubits_required: number
  circuit_depth: number
  gate_count: number
  cx_gate_ratio: number
  superposition_score: number
  entanglement_score: number
  time_complexity: TimeComplexity
  memory_requirement_mb: number
}

export interface HardwareRecommendation {
  recommended_hardware: HardwareType
  confidence: number
  quantum_probability: number
  classical_probability: number
  rationale: string
}

export interface Alternative {
  hardware: string
  confidence: number
  trade_off: string
}

export interface DecisionEngineResponse {
  success: boolean
  recommendation: HardwareRecommendation | null
  alternatives: Alternative[] | null
  estimated_execution_time_ms: number | null
  estimated_cost_usd: number | null
  error: string | null
}

export interface HealthCheckResponse {
  status: string
  model_loaded: boolean
  model_type: string | null
  model_accuracy: number | null
}

// ── Decision History & Feedback Types ──

export interface DecisionLogEntry {
  id: string
  userId: string
  input: CodeAnalysisInput
  prediction: {
    recommended_hardware: string
    confidence: number
    quantum_probability: number
    classical_probability: number
    rationale: string
  }
  estimated_execution_time_ms: number | null
  estimated_cost_usd: number | null
  alternatives: Alternative[] | null
  budget_limit_usd: number | null
  status: 'predicted' | 'executed' | 'failed'
  feedback: {
    actual_hardware_used: string | null
    actual_execution_time_ms: number | null
    actual_cost_usd: number | null
    prediction_correct: boolean | null
    notes: string | null
  } | null
  createdAt: string
  updatedAt: string
}

export interface DecisionHistoryResponse {
  decisions: DecisionLogEntry[]
  total: number
  limit: number
  offset: number
  hasMore: boolean
}

export interface FeedbackInput {
  actual_hardware_used: string
  actual_execution_time_ms: number
  actual_cost_usd: number
  notes?: string
}

export interface AccuracyStats {
  totalPredictions: number
  totalWithFeedback: number
  correctPredictions: number
  accuracy: number
  hardwareBreakdown: Record<string, { total: number; correct: number; accuracy: number }>
  averageCostSavings: number
  averageTimeDelta: number
}

export interface DashboardStats {
  metrics: {
    decisionAccuracy: number
    totalDecisions: number
    totalWithFeedback: number
    costSavings: number
    avgResponseTime: number
  }
  recentDecisions: Array<{
    id: string
    hardware: string
    confidence: number
    status: string
    cost: number | null
    createdAt: string
  }>
  weeklyDistribution: Array<{
    day: string
    quantum: number
    classical: number
    hybrid: number
  }>
}
