
import api from '@/lib/axios';
import type {
  HardwareDevicesResponse,
  HardwareStatusResponse,
  ProvidersResponse,
  QuantumExecuteRequest,
  PythonCodeExecuteRequest,
  ClassicalExecuteRequest,
  ScheduleJobRequest,
  JobSubmissionResponse,
  JobStatusResponse,
  JobResultResponse,
  ScheduledJobsResponse,
  CancelJobResponse,
  DeviceAvailabilityResponse,
} from '@/types/hardware';

const API_BASE = '/v1/hardware';

export const hardwareService = {

  // ===========================================================================
  // Status & Discovery
  // ===========================================================================

  /** Get overall hardware layer status. */
  async getStatus(): Promise<HardwareStatusResponse> {
    const { data } = await api.get<HardwareStatusResponse>(`${API_BASE}/status`);
    return data;
  },

  /** List all available hardware devices from all providers. */
  async getDevices(): Promise<HardwareDevicesResponse> {
    const { data } = await api.get<HardwareDevicesResponse>(`${API_BASE}/devices`);
    return data;
  },

  /** List all registered provider names. */
  async listProviders(): Promise<ProvidersResponse> {
    const { data } = await api.get<ProvidersResponse>(`${API_BASE}/providers`);
    return data;
  },

  /** List devices for a specific provider. */
  async listProviderDevices(provider: string): Promise<HardwareDevicesResponse> {
    const { data } = await api.get<HardwareDevicesResponse>(
      `${API_BASE}/quantum/${provider}/devices`,
    );
    return data;
  },

  // ===========================================================================
  // Quantum Execution
  // ===========================================================================

  /**
   * Submit a QASM circuit to a quantum provider for execution.
   *
   * @param provider  - Provider name (e.g. "ibm-quantum")
   * @param request   - Circuit details (QASM, device, shots, priority, strategy)
   */
  async submitQuantumCircuit(
    provider: string,
    request: QuantumExecuteRequest,
  ): Promise<JobSubmissionResponse> {
    const { data } = await api.post<JobSubmissionResponse>(
      `${API_BASE}/quantum/${provider}/execute`,
      { qasm: request.qasm },
      {
        params: {
          device_name: request.device_name,
          shots: request.shots,
          priority: request.priority,
          strategy: request.strategy,
        },
      },
    );
    return data;
  },

  /**
   * Submit raw Python code for execution on IBM Quantum.
   * The code must define a `circuit` variable that is a QuantumCircuit.
   */
  async submitPythonCode(
    request: PythonCodeExecuteRequest,
  ): Promise<JobSubmissionResponse> {
    const { data } = await api.post<JobSubmissionResponse>(
      `${API_BASE}/quantum/execute-python`,
      request,
    );
    return data;
  },

  // ===========================================================================
  // Classical Execution
  // ===========================================================================

  /**
   * Submit a classical compute task (Python code) to a classical provider.
   *
   * @param provider  - Provider name (e.g. "local", "ibm-classical")
   * @param request   - Task details (code, language, entry_point, parameters)
   */
  async submitClassicalTask(
    provider: string,
    request: ClassicalExecuteRequest,
  ): Promise<JobSubmissionResponse> {
    const { code, language, entry_point, parameters, ...queryParams } = request;
    const { data } = await api.post<JobSubmissionResponse>(
      `${API_BASE}/classical/${provider}/execute`,
      { code, language, entry_point, parameters },
      {
        params: {
          device_name: queryParams.device_name,
          priority: queryParams.priority,
          strategy: queryParams.strategy,
        },
      },
    );
    return data;
  },

  // ===========================================================================
  // Job Scheduling
  // ===========================================================================

  /** Schedule a quantum job for future execution. */
  async scheduleJob(request: ScheduleJobRequest): Promise<JobSubmissionResponse> {
    const { data } = await api.post<JobSubmissionResponse>(
      `${API_BASE}/quantum/schedule`,
      request,
    );
    return data;
  },

  /** List all scheduled jobs waiting for execution. */
  async getScheduledJobs(): Promise<ScheduledJobsResponse> {
    const { data } = await api.get<ScheduledJobsResponse>(
      `${API_BASE}/quantum/scheduled-jobs`,
    );
    return data;
  },

  /** Cancel a scheduled job before it executes. */
  async cancelScheduledJob(jobId: string): Promise<CancelJobResponse> {
    const { data } = await api.delete<CancelJobResponse>(
      `${API_BASE}/quantum/scheduled-jobs/${jobId}`,
    );
    return data;
  },

  // ===========================================================================
  // Device Availability
  // ===========================================================================

  /** Check if a specific IBM Quantum device is available for job submission. */
  async checkDeviceAvailability(device: string): Promise<DeviceAvailabilityResponse> {
    const { data } = await api.get<DeviceAvailabilityResponse>(
      `${API_BASE}/quantum/devices/${device}/availability`,
    );
    return data;
  },

  // ===========================================================================
  // Job Status & Results (generic — works for quantum and classical)
  // ===========================================================================

  /** Get the current status of a job. */
  async getJobStatus(provider: string, jobId: string): Promise<JobStatusResponse> {
    const { data } = await api.get<JobStatusResponse>(
      `${API_BASE}/jobs/${provider}/${jobId}`,
    );
    return data;
  },

  /** Get the result of a completed job. */
  async getJobResult(provider: string, jobId: string): Promise<JobResultResponse> {
    const { data } = await api.get<JobResultResponse>(
      `${API_BASE}/jobs/${provider}/${jobId}/result`,
    );
    return data;
  },
};
