import { useLocation, useNavigate } from 'react-router-dom'
import { MainLayout } from '@/components/layout/MainLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Code, Zap, TrendingUp, Activity, CheckCircle2, XCircle, Clock, Cpu, BarChart3, Info, ArrowLeft, Download, Image as ImageIcon, Play } from 'lucide-react'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { toast } from 'sonner'
import type { ConversionResult } from '@/types/code-converstion.tp'

export default function CodeConversionResults() {
  const location = useLocation()
  const navigate = useNavigate()

  const state = location.state as { results?: ConversionResult } | null
  const results = state?.results
  const result: ConversionResult = results || {
    metadata: { timestamp: new Date().toISOString(), shots: 1000, gateType: 'Auto-detected' },
    pythonCode: 'No data available',
    quantumCode: 'No data available',
    executionResults: {
      success: false,
      used_generated_code: false,
      counts: {},
      probabilities: {},
      performance: { depth: 0, num_qubits: 0, num_gates: 0, gate_counts: {}, execution_time_seconds: 0 },
    },
  }

  if (!results) {
    return (
      <MainLayout title="No Results Found">
        <div className="text-center py-12">
          <h1 className="text-2xl font-semibold mb-4 text-ink">No Results Found</h1>
          <p className="text-ink-muted mb-6">Please run a conversion first to see results.</p>
          <Button onClick={() => navigate('/ai-converter')}>Go to Converter</Button>
        </div>
      </MainLayout>
    )
  }

  const getQualityText = () => {
    if (!result.executionResults.success) return 'Failed'
    if (result.executionResults.used_generated_code) return 'Good'
    return 'Fallback Used'
  }

  const calculateSpeedComparison = () => {
    if (!result.pythonPerformance) return null

    const quantumTimePerOp = (result.executionResults.performance.execution_time_seconds / result.metadata.shots) * 1000
    const pythonTimePerOp = result.pythonPerformance.estimatedPerOp

    const speedFactor = pythonTimePerOp / quantumTimePerOp
    const faster = speedFactor > 1 ? 'Python' : 'Quantum'
    const factor = Math.max(speedFactor, 1 / speedFactor).toFixed(1)

    return {
      faster,
      factor,
      quantumTimePerOp: quantumTimePerOp.toFixed(6),
      pythonTimePerOp: pythonTimePerOp.toFixed(6),
      summary: `${faster} is ${factor}x faster`,
    }
  }

  const speedComparison = calculateSpeedComparison()

  const displayImage = (base64String: string, title: string) => {
    if (!base64String) return null

    return (
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <ImageIcon className="h-4 w-4 text-ink" />
          <span className="font-medium text-ink">{title}</span>
        </div>
        <img src={`data:image/png;base64,${base64String}`} alt={title} className="w-full border border-hairline max-h-[400px] object-contain" />
      </div>
    )
  }

  const exportAllData = () => {
    const exportData = { ...result, export_timestamp: new Date().toISOString(), export_format: 'JSON v2.0' }

    const dataStr = JSON.stringify(exportData, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `quantum_conversion_full_${new Date().getTime()}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    toast.success('All data exported as JSON')
  }

  const mostProbableState = Object.entries(result.executionResults.probabilities || {}).sort((a, b) => b[1] - a[1])[0]
  const totalUniqueStates = Object.keys(result.executionResults.counts || {}).length

  return (
    <MainLayout title="Conversion Results" description="Complete analysis of quantum code conversion">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Button variant="outline" onClick={() => navigate('/ai-converter')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Converter
          </Button>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => navigate('/ai-converter', { state: { results } })}>
              <Play className="mr-2 h-4 w-4" />
              Re-run
            </Button>
            <Button onClick={exportAllData}>
              <Download className="mr-2 h-4 w-4" />
              Export All
            </Button>
          </div>
        </div>

        <Alert variant={result.executionResults.success ? 'success' : 'destructive'}>
          {result.executionResults.success ? <CheckCircle2 className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
          <AlertTitle>{result.executionResults.success ? 'Conversion Successful' : 'Conversion Failed'}</AlertTitle>
          <AlertDescription>
            {speedComparison?.summary || 'Performance comparison available'}
            {result.executionResults.fallback_reason && <div className="mt-2 text-sm">Fallback used: {result.executionResults.fallback_reason}</div>}
          </AlertDescription>
        </Alert>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Execution Time</CardTitle>
              <Clock className="h-4 w-4 text-ink-muted" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-semibold text-ink">{(result.executionResults.performance.execution_time_seconds * 1000).toFixed(2)}ms</div>
              <p className="text-xs text-ink-muted">{result.metadata.shots} shots</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Circuit Complexity</CardTitle>
              <Activity className="h-4 w-4 text-ink-muted" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-semibold text-ink">{result.executionResults.performance.num_gates}</div>
              <p className="text-xs text-ink-muted">
                {result.executionResults.performance.num_qubits} qubits • Depth: {result.executionResults.performance.depth}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Translation Quality</CardTitle>
              <TrendingUp className="h-4 w-4 text-ink-muted" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-semibold text-ink">{getQualityText()}</div>
              <Badge variant={result.executionResults.success ? 'success' : 'destructive'} className="mt-1">
                {result.executionResults.success ? 'Success' : 'Failed'}
              </Badge>
            </CardContent>
          </Card>
        </div>

        {result.executionResults.images && (
          <Card>
            <CardHeader>
              <CardTitle>Visualizations</CardTitle>
              <CardDescription>Generated circuit diagrams and measurements</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {result.executionResults.images.circuit_diagram && displayImage(result.executionResults.images.circuit_diagram, 'Quantum Circuit')}
                {result.executionResults.images.measurement_histogram &&
                  displayImage(result.executionResults.images.measurement_histogram, 'Measurement Histogram')}
              </div>
            </CardContent>
          </Card>
        )}

        <Tabs defaultValue="code" className="space-y-4">
          <TabsList>
            <TabsTrigger value="code">Code</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="quantum">Quantum Analysis</TabsTrigger>
            <TabsTrigger value="probability">Measurement Results</TabsTrigger>
          </TabsList>

          <TabsContent value="code" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Code className="h-5 w-5" />
                    Original Python Code
                  </CardTitle>
                  <CardDescription>Input classical code</CardDescription>
                </CardHeader>
                <CardContent>
                  <pre className="bg-surface-1 border border-hairline p-4 overflow-x-auto max-h-[300px]">
                    <code className="text-sm font-mono whitespace-pre text-ink">{result.pythonCode}</code>
                  </pre>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Zap className="h-5 w-5" />
                    Generated Quantum Code
                  </CardTitle>
                  <CardDescription>Qiskit implementation</CardDescription>
                </CardHeader>
                <CardContent>
                  <pre className="bg-surface-1 border border-hairline p-4 overflow-x-auto max-h-[300px]">
                    <code className="text-sm font-mono whitespace-pre text-ink">{result.quantumCode}</code>
                  </pre>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="performance" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  Performance Comparison
                </CardTitle>
                <CardDescription>{speedComparison?.summary || 'Performance analysis'}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-3">
                    <h4 className="font-semibold text-sm flex items-center gap-2 text-quantum">
                      <Cpu className="h-4 w-4" />
                      Quantum Simulation
                    </h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-ink-muted">Execution Time:</span>
                        <span className="font-mono font-medium text-ink">{(result.executionResults.performance.execution_time_seconds * 1000).toFixed(3)} ms</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-ink-muted">Shots Executed:</span>
                        <span className="font-mono font-medium text-ink">{result.metadata.shots.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-ink-muted">Shots/Second:</span>
                        <span className="font-mono font-medium text-ink">
                          {result.metadata.shots / result.executionResults.performance.execution_time_seconds > 0
                            ? Math.round(result.metadata.shots / result.executionResults.performance.execution_time_seconds).toLocaleString()
                            : 'N/A'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-ink-muted">Time per Shot:</span>
                        <span className="font-mono font-medium text-ink">{speedComparison?.quantumTimePerOp || 'N/A'} ms</span>
                      </div>
                    </div>
                  </div>

                  {result.pythonPerformance && (
                    <div className="space-y-3">
                      <h4 className="font-semibold text-sm flex items-center gap-2 text-classical">
                        <Code className="h-4 w-4" />
                        Python Execution (Estimated)
                      </h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-ink-muted">Ops/Second:</span>
                          <span className="font-mono font-medium text-ink">{result.pythonPerformance.estimatedOpsPerSecond.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-ink-muted">Time per Operation:</span>
                          <span className="font-mono font-medium text-ink">{result.pythonPerformance.estimatedPerOp.toFixed(4)} ms</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-ink-muted">Equivalent Shots:</span>
                          <span className="font-mono font-medium text-ink">
                            ~
                            {Math.round(
                              result.pythonPerformance.estimatedOpsPerSecond * result.executionResults.performance.execution_time_seconds
                            ).toLocaleString()}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-ink-muted">Speed Factor:</span>
                          <span className="font-mono font-medium text-ink">{Math.round(result.pythonPerformance.speedDifference).toLocaleString()}x</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {result.pythonPerformance && speedComparison && (
                  <div className="space-y-4">
                    <div className="flex justify-between text-sm">
                      <span className="font-medium text-ink">Speed Advantage</span>
                      <span className="font-medium text-primary">
                        {speedComparison.faster} is {speedComparison.factor}x faster
                      </span>
                    </div>
                    <div className="relative h-10 bg-surface-2 overflow-hidden">
                      <div
                        className="absolute inset-y-0 flex items-center justify-center text-on-primary text-sm font-medium transition-all duration-1000 bg-primary"
                        style={{
                          width: speedComparison.faster === 'Quantum' ? '70%' : '30%',
                          [speedComparison.faster === 'Quantum' ? 'left' : 'right']: 0,
                        }}
                      >
                        {speedComparison.faster === 'Quantum' ? 'Quantum' : 'Python'}
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

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
                      <span className="text-sm text-ink-muted">Number of Qubits:</span>
                      <Badge variant="outline" className="font-mono">
                        {result.executionResults.performance.num_qubits}
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-ink-muted">Circuit Depth:</span>
                      <Badge variant="outline" className="font-mono">
                        {result.executionResults.performance.depth}
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-ink-muted">Total Gates:</span>
                      <Badge variant="outline" className="font-mono">
                        {result.executionResults.performance.num_gates}
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-ink-muted">Unique States:</span>
                      <Badge variant="outline" className="font-mono">
                        {totalUniqueStates}
                      </Badge>
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
                  {Object.entries(result.executionResults.performance.gate_counts || {}).map(([gate, count]) => (
                    <div key={gate} className="space-y-1">
                      <div className="flex justify-between text-sm text-ink">
                        <span className="font-mono uppercase">{gate}</span>
                        <span className="text-ink-muted">{count} gates</span>
                      </div>
                      <Progress value={(count / result.executionResults.performance.num_gates) * 100} className="h-2" />
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
                    <span className="text-ink-muted block mb-1">Timestamp:</span>
                    <span className="font-mono text-ink">{new Date(result.metadata.timestamp).toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-ink-muted block mb-1">Shots Executed:</span>
                    <span className="font-mono text-ink">{result.metadata.shots.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-ink-muted block mb-1">Most Probable State:</span>
                    <Badge className="font-mono">{mostProbableState ? `|${mostProbableState[0]}⟩` : 'N/A'}</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="probability" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  State Probability Distribution
                </CardTitle>
                <CardDescription>Measurement outcomes from {result.metadata.shots} shots</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {Object.entries(result.executionResults.probabilities || {})
                  .sort(([, a], [, b]) => b - a)
                  .map(([state, probability]) => (
                    <div key={state} className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="font-mono">
                            |{state}⟩
                          </Badge>
                          <span className="text-ink-muted">{result.executionResults.counts[state]} counts</span>
                        </div>
                        <span className="font-medium text-ink">{(probability * 100).toFixed(1)}%</span>
                      </div>
                      <Progress value={probability * 100} className="h-3" />
                    </div>
                  ))}
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <div className="text-2xl font-semibold text-ink">{totalUniqueStates}</div>
                    <div className="text-sm text-ink-muted">Unique States</div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <div className="text-2xl font-semibold text-ink">{mostProbableState ? `${(mostProbableState[1] * 100).toFixed(1)}%` : 'N/A'}</div>
                    <div className="text-sm text-ink-muted">Most Probable: {mostProbableState ? `|${mostProbableState[0]}⟩` : ''}</div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <div className="text-2xl font-semibold text-ink">{result.metadata.shots}</div>
                    <div className="text-sm text-ink-muted">Total Shots</div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  )
}
