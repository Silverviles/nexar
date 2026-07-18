export interface HardwareDevice {
  name: string
  provider: string
  type?: string
  description?: string
  version?: string
  // Quantum specific
  num_qubits?: number
  is_simulator?: boolean
  is_operational?: boolean
  pending_jobs?: number
  basis_gates?: Array<{
    name: string
    description: string
    qiskit_name: string
  }>
  coupling_map?: Record<string, number[]>
  // Classical specific
  status?: string
}

export interface HardwareStatusResponse {
  status: string
  service: string
  providers_available: number
  providers: string[]
}

export interface HardwareDevicesResponse {
  devices: HardwareDevice[]
}

export interface ProvidersResponse {
  providers: string[]
}

export type JobPriority = 'high' | 'standard'
export type OptimizationStrategy = 'time' | 'cost'

export interface QuantumExecuteRequest {
  qasm: string
  device_name: string
  shots?: number
  priority?: JobPriority
  strategy?: OptimizationStrategy
}

export interface PythonCodeExecuteRequest {
  code: string
  device_name: string
  shots?: number
  queue_if_unavailable?: boolean
  scheduled_time?: string
}

export interface ClassicalExecuteRequest {
  code: string
  language?: string
  entry_point?: string
  parameters?: Record<string, unknown>
  device_name?: string
  priority?: JobPriority
  strategy?: OptimizationStrategy
}

export interface ScheduleJobRequest {
  device_name: string
  scheduled_time: string
  circuit?: { qasm: string }
  code?: string
  shots?: number
  queue_if_unavailable?: boolean
}

export interface JobSubmissionResponse {
  job_id: string
  status: 'PENDING' | 'SCHEDULED' | 'QUEUED_UNAVAILABLE'
  type: 'quantum' | 'classical'
  provider: string
  device: string
  scheduled_for?: string
  queued_reason?: string
}

export interface JobStatusResponse {
  job_id: string
  provider: string
  status: string
  state?: string
  /** Failure reason, present only when status is "FAILED". */
  error?: string
}

export interface JobResultResponse {
  job_id: string
  provider: string
  result: Record<string, unknown> | null
}

export interface ScheduledJobsResponse {
  scheduled_jobs: Array<Record<string, unknown>>
  count: number
}

export interface CancelJobResponse {
  job_id: string
  status: 'CANCELLED'
}

export interface DeviceAvailabilityResponse {
  device_name: string
  is_operational: boolean
  pending_jobs: number
  queue_threshold: number
  is_available: boolean
}
