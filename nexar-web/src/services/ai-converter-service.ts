import api from '@/lib/axios'
import { toast } from 'sonner'

export interface TranslationResponse {
  quantum_code: string
}

export interface ExecutionRequest {
  quantum_code: string
  gate_type?: string
  shots?: number
}

export interface ExecutionResponse {
  success: boolean
  data?: unknown
  performance?: {
    execution_time_seconds: number
    depth?: number
    num_qubits?: number
  }
}

export interface PythonPerformance {
  estimatedOpsPerSecond: number
  estimatedPerOp: number
  speedDifference: number
}

export interface FullFlowResults {
  metadata: {
    timestamp: string
    shots: number
    gateType: string
  }
  pythonCode: string
  quantumCode: string
  executionResults: ExecutionResponse
  pythonPerformance: PythonPerformance | null
}

class QuantumService {
  async translatePythonToQuantum(pythonCode: string): Promise<string> {
    try {
      const response = await api.post<TranslationResponse>('/v1/ai-code-converter/translate', {
        python_code: pythonCode,
      })
      return response.data.quantum_code
    } catch (error: any) {
      console.error('Translation error:', error)
      throw new Error(error.response?.data?.message || 'Translation failed')
    }
  }

  async executeQuantumCode(quantumCode: string, shots: number = 1000): Promise<ExecutionResponse> {
    try {
      const response = await api.post<ExecutionResponse>('/v1/ai-code-converter/execute', {
        quantum_code: quantumCode,
        gate_type: 'auto',
        shots,
      })
      return response.data
    } catch (error: any) {
      console.error('Execution error:', error)
      throw new Error(error.response?.data?.message || 'Execution failed')
    }
  }

  estimatePythonPerformance(quantumExecutionTime: number | null): PythonPerformance | null {
    if (!quantumExecutionTime) return null

    const estimatedOpsPerSecond = 10_000_000
    const estimatedPerOp = 0.0001

    const quantumTime = quantumExecutionTime * 1000
    const quantumPerShot = quantumTime / 1000

    return {
      estimatedOpsPerSecond,
      estimatedPerOp,
      speedDifference: quantumPerShot / estimatedPerOp,
    }
  }

  async executeFullFlow(pythonCode: string, shots: number = 1000): Promise<FullFlowResults> {
    if (!pythonCode.trim()) {
      throw new Error('Python code is required')
    }

    try {
      toast.info('Starting full conversion flow...')

      toast.info('Translating Python to quantum code...')
      const quantumCode = await this.translatePythonToQuantum(pythonCode)

      const quantumCodeWithImports = quantumCode.startsWith('from qiskit')
        ? quantumCode
        : `from qiskit import QuantumCircuit\n${quantumCode}`

      toast.success('Translation successful!')

      toast.info('Executing quantum circuit...')
      const executionResults = await this.executeQuantumCode(quantumCodeWithImports, shots)

      if (!executionResults.success) {
        throw new Error('Quantum execution failed')
      }

      toast.success('Execution successful!')

      toast.info('Analyzing performance...')
      const pythonPerformance = this.estimatePythonPerformance(
        executionResults.performance?.execution_time_seconds ?? null
      )

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
      }

      toast.success('Full flow completed!')
      return completeResults
    } catch (error: any) {
      console.error('Full flow error:', error)
      toast.error(`Error: ${error.message || 'Failed to complete conversion'}`)
      throw error
    }
  }
}

export default new QuantumService()
