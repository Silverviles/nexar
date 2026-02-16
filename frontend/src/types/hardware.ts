
export interface HardwareDevice {
  name: string;
  provider: string;
  type?: string;
  description?: string;
  version?: string;
  // Quantum specific
  num_qubits?: number;
  is_simulator?: boolean;
  is_operational?: boolean;
  pending_jobs?: number;
  basis_gates?: Array<{
    name: string;
    description: string;
    qiskit_name: string;
  }>;
  coupling_map?: Record<string, number[]>;
  // Classical specific
  status?: string;
}

export interface HardwareStatusResponse {
  status: string;
  service: string;
  providers_available: number;
  providers: string[];
}

export interface HardwareDevicesResponse {
  devices: HardwareDevice[];
}

// ---------------------------------------------------------------------------
// Providers
// ---------------------------------------------------------------------------

export interface ProvidersResponse {
  providers: string[];
}

// ---------------------------------------------------------------------------
// Job Submission — Request types
// ---------------------------------------------------------------------------

export type JobPriority = 'high' | 'standard';
export type OptimizationStrategy = 'time' | 'cost';

/** Submit a QASM circuit to a quantum provider. */
export interface QuantumExecuteRequest {
  /** OpenQASM string representing the circuit. */
  qasm: string;
  /** Target device name (e.g. "ibm_brisbane"). */
  device_name: string;
  /** Number of measurement shots. */
  shots?: number;
  priority?: JobPriority;
  strategy?: OptimizationStrategy;
}

/** Submit raw Python code that builds a QuantumCircuit. */
export interface PythonCodeExecuteRequest {
  /** Python source code — must define a `circuit` variable. */
  code: string;
  /** Target IBM Quantum device name. */
  device_name: string;
  shots?: number;
  /** Queue the job if the device is currently unavailable. */
  queue_if_unavailable?: boolean;
  /** ISO-8601 datetime string to schedule execution for. */
  scheduled_time?: string;
}

/** Submit a classical compute task (Python code). */
export interface ClassicalExecuteRequest {
  /** Python source code. */
  code: string;
  language?: string;
  entry_point?: string;
  parameters?: Record<string, unknown>;
  device_name?: string;
  priority?: JobPriority;
  strategy?: OptimizationStrategy;
}

/** Schedule a quantum job for future execution. */
export interface ScheduleJobRequest {
  device_name: string;
  /** ISO-8601 datetime string — must be in the future. */
  scheduled_time: string;
  /** Either a QASM circuit string … */
  circuit?: { qasm: string };
  /** … or raw Python code (mutually exclusive with circuit). */
  code?: string;
  shots?: number;
  queue_if_unavailable?: boolean;
}

// ---------------------------------------------------------------------------
// Job Submission — Response types
// ---------------------------------------------------------------------------

/** Returned by all job submission endpoints (quantum & classical). */
export interface JobSubmissionResponse {
  job_id: string;
  status: 'PENDING' | 'SCHEDULED' | 'QUEUED_UNAVAILABLE';
  type: 'quantum' | 'classical';
  provider: string;
  device: string;
  /** Present when the job is scheduled for future execution. */
  scheduled_for?: string;
  /** Present when the job was queued due to device unavailability. */
  queued_reason?: string;
}

// ---------------------------------------------------------------------------
// Job Status & Results
// ---------------------------------------------------------------------------

export interface JobStatusResponse {
  job_id: string;
  provider: string;
  status: string;
}

export interface JobResultResponse {
  job_id: string;
  provider: string;
  result: Record<string, unknown> | null;
}

// ---------------------------------------------------------------------------
// Scheduling
// ---------------------------------------------------------------------------

export interface ScheduledJobsResponse {
  scheduled_jobs: Array<Record<string, unknown>>;
  count: number;
}

export interface CancelJobResponse {
  job_id: string;
  status: 'CANCELLED';
}

// ---------------------------------------------------------------------------
// Device Availability
// ---------------------------------------------------------------------------

export interface DeviceAvailabilityResponse {
  device_name: string;
  is_operational: boolean;
  pending_jobs: number;
  queue_threshold: number;
  is_available: boolean;
}
