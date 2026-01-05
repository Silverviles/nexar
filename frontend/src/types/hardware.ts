
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
