import api from '@/lib/axios';
import { toast } from 'sonner';

export interface TranslationResponse {
  quantum_code: string;
}

export interface ExecutionRequest {
  quantum_code: string;
  gate_type?: string;
  shots?: number;
}

export interface ExecutionResponse {
  success: boolean;
  data?: any;
  performance?: {
    execution_time_seconds: number;
  };
}

export interface PythonPerformance {
  estimatedOpsPerSecond: number;
  estimatedPerOp: number;
  speedDifference: number;
}

export interface FullFlowResults {
  metadata: {
    timestamp: string;
    shots: number;
    gateType: string;
  };
  pythonCode: string;
  quantumCode: string;
  executionResults: ExecutionResponse;
  pythonPerformance: PythonPerformance | null;
}

class QuantumService {
  async translatePythonToQuantum(pythonCode: string): Promise<string> {
    try {
      const response = await api.post<TranslationResponse>('/translate', {
        python_code: pythonCode,
      });
      return response.data.quantum_code;
    } catch (error: any) {
      console.error('Translation error:', error);
      throw new Error(error.response?.data?.message || 'Translation failed');
    }
  }

  // Execute quantum code
  async executeQuantumCode(quantumCode: string, shots: number = 1000): Promise<ExecutionResponse> {
    try {
      const response = await api.post<ExecutionResponse>('/execute', {
        quantum_code: quantumCode,
        gate_type: 'auto',
        shots,
      });
      return response.data;
    } catch (error: any) {
      console.error('Execution error:', error);
      throw new Error(error.response?.data?.message || 'Execution failed');
    }
  }

  // Estimate Python performance
  estimatePythonPerformance(quantumExecutionTime: number | null): PythonPerformance | null {
    if (!quantumExecutionTime) return null;

    const estimatedOpsPerSecond = 10_000_000; // 10M ops/sec
    const estimatedPerOp = 0.0001; // 0.1µs per operation

    // Calculate quantum stats (convert to ms if needed)
    const quantumTime = quantumExecutionTime * 1000; // ms
    const quantumPerShot = quantumTime / 1000; // ms per shot

    return {
      estimatedOpsPerSecond,
      estimatedPerOp,
      speedDifference: quantumPerShot / estimatedPerOp,
    };
  }

  // Execute full conversion flow
  async executeFullFlow(pythonCode: string, shots: number = 1000): Promise<FullFlowResults> {
    if (!pythonCode.trim()) {
      throw new Error('Python code is required');
    }

    try {
      toast.info('Starting full conversion flow...');

      // Step 1: Translate Python to Quantum
      toast.info('Translating Python to quantum code...');
      const quantumCode = await this.translatePythonToQuantum(pythonCode);
      
      const quantumCodeWithImports = quantumCode.startsWith('from qiskit')
        ? quantumCode
        : `from qiskit import QuantumCircuit\n${quantumCode}`;

      toast.success('Translation successful!');

      // Step 2: Execute quantum circuit
      toast.info('Executing quantum circuit...');
      const executionResults = await this.executeQuantumCode(quantumCodeWithImports, shots);
      
      if (!executionResults.success) {
        throw new Error('Quantum execution failed');
      }

      toast.success('Execution successful!');

      // Step 3: Estimate Python performance
      toast.info('Analyzing performance...');
      const pythonPerformance = this.estimatePythonPerformance(
        executionResults.performance?.execution_time_seconds
      );

      // Step 4: Prepare complete results
      const completeResults: FullFlowResults = {
        metadata: {
          timestamp: new Date().toISOString(),
          shots,
          gateType: 'Auto-detected',
        },
        pythonCode,
        quantumCode: quantumCodeWithImports,
        executionResults,
        pythonPerformance,
      };

      toast.success('Full flow completed!');
      return completeResults;
    } catch (error: any) {
      console.error('Full flow error:', error);
      toast.error(`Error: ${error.message || 'Failed to complete conversion'}`);
      throw error;
    }
  }
}


// Export as singleton instance
export default new QuantumService();