import { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { 
  Code, 
  Zap, 
  TrendingUp, 
  Activity, 
  CheckCircle2, 
  XCircle, 
  Clock,
  Cpu,
  BarChart3,
  Info
} from 'lucide-react';
import { Progress } from '@/components/ui/progress';

interface ConversionResult {
  test_metadata: {
    gate_type: string;
    test_timestamp: string;
    shots_executed: number;
    server_url: string;
  };
  original_python_code: string;
  translation_results: {
    raw_quantum_code: string;
    quantum_code_with_imports: string;
    translation_success: boolean;
  };
  quantum_execution: {
    success: boolean;
    used_generated_code: boolean;
    fallback_reason: string | null;
    counts: Record<string, number>;
    probabilities: Record<string, number>;
    circuit_analysis: {
      depth: number;
      num_qubits: number;
      num_gates: number;
      gate_counts: Record<string, number>;
      execution_time_seconds: number;
    };
  };
  performance_comparison: {
    quantum_simulation: {
      execution_time_seconds: number;
      execution_time_ms: number;
      shots: number;
      shots_per_second: number;
    };
    python_execution: {
      execution_time_ms: number;
      execution_time_seconds: number;
      operations: number;
      operations_per_second: number;
      time_per_operation_ns: number;
    };
    speed_comparison: {
      python_vs_quantum_speed_ratio: number;
      quantum_time_per_shot_ms: number;
      python_time_per_operation_ns: number;
      python_is_faster_by_factor: number;
      faster_implementation: string;
    };
    comparison_summary: string;
  };
  summary: {
    gate_type_tested: string;
    circuit_complexity: string;
    total_unique_states: number;
    most_probable_state: string;
    translation_quality: string;
  };
}

// Mock data - in real implementation, this would come from API
const mockResult: ConversionResult = {
  test_metadata: {
    gate_type: "NOR",
    test_timestamp: "2025-12-18 13:32:43",
    shots_executed: 1000,
    server_url: "http://127.0.0.1:8000"
  },
  original_python_code: "def nor_gate(a, b): return 1 - (a | b)",
  translation_results: {
    raw_quantum_code: "qc = QuantumCircuit(2, 2)\nqc.h(0)\nqc.h(1)\nqc.x(0)\nqc.cx(0,1)\nqc.measure([0,1],[0,1])",
    quantum_code_with_imports: "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2, 2)\nqc.h(0)\nqc.h(1)\nqc.x(0)\nqc.cx(0,1)\nqc.measure([0,1],[0,1])",
    translation_success: true
  },
  quantum_execution: {
    success: true,
    used_generated_code: true,
    fallback_reason: null,
    counts: {
      "11": 257,
      "00": 254,
      "01": 259,
      "10": 230
    },
    probabilities: {
      "11": 0.257,
      "00": 0.254,
      "01": 0.259,
      "10": 0.23
    },
    circuit_analysis: {
      depth: 4,
      num_qubits: 2,
      num_gates: 6,
      gate_counts: {
        "h": 2,
        "measure": 2,
        "x": 1,
        "cx": 1
      },
      execution_time_seconds: 0.004038810729980469
    }
  },
  performance_comparison: {
    quantum_simulation: {
      execution_time_seconds: 0.004038810729980469,
      execution_time_ms: 4.038810729980469,
      shots: 1000,
      shots_per_second: 247597.63872491146
    },
    python_execution: {
      execution_time_ms: 289.34769999978016,
      execution_time_seconds: 0.28934769999978016,
      operations: 4000000,
      operations_per_second: 13824198.36066794,
      time_per_operation_ns: 72.33692499994504
    },
    speed_comparison: {
      python_vs_quantum_speed_ratio: 55.83332067244408,
      quantum_time_per_shot_ms: 0.004038810729980469,
      python_time_per_operation_ns: 72.33692499994504,
      python_is_faster_by_factor: 0.013958330168111021,
      faster_implementation: "Quantum"
    },
    comparison_summary: "Quantum simulation is 71.6x faster than Python"
  },
  summary: {
    gate_type_tested: "NOR",
    circuit_complexity: "Simple",
    total_unique_states: 4,
    most_probable_state: "01",
    translation_quality: "Good"
  }
};

export default function CodeConversionResults() {
  const [result] = useState<ConversionResult>(mockResult);

  const getQualityColor = (quality: string) => {
    const colors = {
      'Good': 'bg-green-500',
      'Excellent': 'bg-blue-500',
      'Fair': 'bg-yellow-500',
      'Poor': 'bg-red-500'
    };
    return colors[quality as keyof typeof colors] || 'bg-gray-500';
  };

  const getComplexityColor = (complexity: string) => {
    const colors = {
      'Simple': 'bg-green-500',
      'Moderate': 'bg-yellow-500',
      'Complex': 'bg-orange-500',
      'Very Complex': 'bg-red-500'
    };
    return colors[complexity as keyof typeof colors] || 'bg-gray-500';
  };

  return (
    <MainLayout 
      title="Code Conversion Results" 
      description="Analysis results from quantum code conversion"
    >
      <div className="space-y-6">
        {/* Status Banner */}
        <Alert className={result.translation_results.translation_success ? "border-green-500" : "border-red-500"}>
          {result.translation_results.translation_success ? (
            <CheckCircle2 className="h-4 w-4 text-green-600" />
          ) : (
            <XCircle className="h-4 w-4 text-red-600" />
          )}
          <AlertTitle>
            {result.translation_results.translation_success ? 'Conversion Successful' : 'Conversion Failed'}
          </AlertTitle>
          <AlertDescription>
            {result.performance_comparison.comparison_summary}
          </AlertDescription>
        </Alert>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Gate Type</CardTitle>
              <Code className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{result.test_metadata.gate_type}</div>
              <p className="text-xs text-muted-foreground">
                {result.summary.circuit_complexity} circuit
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Execution Time</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {result.quantum_execution.circuit_analysis.execution_time_seconds.toFixed(4)}s
              </div>
              <p className="text-xs text-muted-foreground">
                {result.performance_comparison.quantum_simulation.execution_time_ms.toFixed(2)}ms
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Circuit Complexity</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{result.quantum_execution.circuit_analysis.num_gates}</div>
              <p className="text-xs text-muted-foreground">
                Gates • Depth: {result.quantum_execution.circuit_analysis.depth}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Translation Quality</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{result.summary.translation_quality}</div>
              <Badge className={`${getQualityColor(result.summary.translation_quality)} text-white mt-1`}>
                Success
              </Badge>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Tabs */}
        <Tabs defaultValue="code" className="space-y-4">
          <TabsList>
            <TabsTrigger value="code">Code</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="quantum">Quantum Analysis</TabsTrigger>
            <TabsTrigger value="probability">Probability Distribution</TabsTrigger>
          </TabsList>

          {/* Code Tab */}
          <TabsContent value="code" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>Original Python Code</CardTitle>
                  <CardDescription>Input classical code</CardDescription>
                </CardHeader>
                <CardContent>
                  <pre className="bg-muted p-4 rounded-lg overflow-x-auto">
                    <code className="text-sm font-mono">{result.original_python_code}</code>
                  </pre>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Generated Quantum Code</CardTitle>
                  <CardDescription>Qiskit implementation</CardDescription>
                </CardHeader>
                <CardContent>
                  <pre className="bg-muted p-4 rounded-lg overflow-x-auto">
                    <code className="text-sm font-mono">{result.translation_results.quantum_code_with_imports}</code>
                  </pre>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Performance Tab */}
          <TabsContent value="performance" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  Performance Comparison
                </CardTitle>
                <CardDescription>
                  {result.performance_comparison.comparison_summary}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Quantum Performance */}
                  <div className="space-y-3">
                    <h4 className="font-semibold text-sm flex items-center gap-2">
                      <Cpu className="h-4 w-4 text-purple-500" />
                      Quantum Simulation
                    </h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Execution Time:</span>
                        <span className="font-mono font-medium">
                          {result.performance_comparison.quantum_simulation.execution_time_ms.toFixed(3)} ms
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Shots Executed:</span>
                        <span className="font-mono font-medium">
                          {result.performance_comparison.quantum_simulation.shots.toLocaleString()}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Shots/Second:</span>
                        <span className="font-mono font-medium">
                          {result.performance_comparison.quantum_simulation.shots_per_second.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Python Performance */}
                  <div className="space-y-3">
                    <h4 className="font-semibold text-sm flex items-center gap-2">
                      <Code className="h-4 w-4 text-blue-500" />
                      Python Execution
                    </h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Execution Time:</span>
                        <span className="font-mono font-medium">
                          {result.performance_comparison.python_execution.execution_time_ms.toFixed(3)} ms
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Operations:</span>
                        <span className="font-mono font-medium">
                          {result.performance_comparison.python_execution.operations.toLocaleString()}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Ops/Second:</span>
                        <span className="font-mono font-medium">
                          {result.performance_comparison.python_execution.operations_per_second.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Speed Comparison Bar */}
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">Speed Advantage</span>
                    <span className="font-medium text-purple-600">
                      {result.performance_comparison.speed_comparison.faster_implementation} is faster
                    </span>
                  </div>
                  <div className="relative h-8 bg-muted rounded-lg overflow-hidden">
                    <div 
                      className="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-500 to-purple-600 flex items-center justify-center text-white text-xs font-medium"
                      style={{ width: '75%' }}
                    >
                      Quantum: {result.performance_comparison.speed_comparison.python_vs_quantum_speed_ratio.toFixed(1)}x
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Quantum Analysis Tab */}
          <TabsContent value="quantum" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>Circuit Properties</CardTitle>
                  <CardDescription>Quantum circuit characteristics</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Number of Qubits:</span>
                      <Badge variant="outline">{result.quantum_execution.circuit_analysis.num_qubits}</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Circuit Depth:</span>
                      <Badge variant="outline">{result.quantum_execution.circuit_analysis.depth}</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Total Gates:</span>
                      <Badge variant="outline">{result.quantum_execution.circuit_analysis.num_gates}</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Unique States:</span>
                      <Badge variant="outline">{result.summary.total_unique_states}</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Gate Composition</CardTitle>
                  <CardDescription>Distribution of quantum gates</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {Object.entries(result.quantum_execution.circuit_analysis.gate_counts).map(([gate, count]) => (
                    <div key={gate} className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="font-mono uppercase">{gate}</span>
                        <span className="text-muted-foreground">{count} gates</span>
                      </div>
                      <Progress 
                        value={(count / result.quantum_execution.circuit_analysis.num_gates) * 100} 
                        className="h-2"
                      />
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Info className="h-5 w-5" />
                  Execution Details
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground block mb-1">Timestamp:</span>
                    <span className="font-mono">{result.test_metadata.test_timestamp}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground block mb-1">Shots Executed:</span>
                    <span className="font-mono">{result.test_metadata.shots_executed.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground block mb-1">Most Probable State:</span>
                    <Badge className="font-mono">{result.summary.most_probable_state}</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Probability Distribution Tab */}
          <TabsContent value="probability" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  State Probability Distribution
                </CardTitle>
                <CardDescription>
                  Measurement outcomes from {result.test_metadata.shots_executed} shots
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {Object.entries(result.quantum_execution.probabilities)
                  .sort(([, a], [, b]) => b - a)
                  .map(([state, probability]) => (
                    <div key={state} className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="font-mono">
                            |{state}⟩
                          </Badge>
                          <span className="text-muted-foreground">
                            {result.quantum_execution.counts[state]} counts
                          </span>
                        </div>
                        <span className="font-medium">
                          {(probability * 100).toFixed(1)}%
                        </span>
                      </div>
                      <Progress value={probability * 100} className="h-3" />
                    </div>
                  ))}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  );
}
