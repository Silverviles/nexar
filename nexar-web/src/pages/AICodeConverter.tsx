import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2, Copy, Check, Eye, Code, Zap, Download, BarChart, Play } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { MainLayout } from '@/components/layout/MainLayout'
import { toast } from 'sonner'
import quantumService, { type FullFlowResults } from '@/services/ai-converter-service'

export default function AICodeConverter() {
  const navigate = useNavigate()
  const [inputCode, setInputCode] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<FullFlowResults | null>(null)
  const [copied, setCopied] = useState(false)

  const executeFullFlow = async () => {
    if (!inputCode.trim() || isLoading) return

    setIsLoading(true)
    setResults(null)

    try {
      const completeResults = await quantumService.executeFullFlow(inputCode)
      setResults(completeResults)
    } catch (error) {
      console.error('Full flow error:', error)
      // Error is already handled in the service with toast notifications
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      toast.success(`${type} copied to clipboard`)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      toast.error('Failed to copy to clipboard')
    }
  }

  const viewDetailedAnalysis = () => {
    if (results) {
      navigate('/conversion-results', { state: { results } })
    }
  }

  const exportResults = () => {
    if (!results) return

    const exportData = { ...results, export_timestamp: new Date().toISOString(), export_format: 'JSON v1.0' }

    const dataStr = JSON.stringify(exportData, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `quantum_conversion_${new Date().getTime()}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    toast.success('Results exported as JSON')
  }

  const resetConverter = () => {
    setInputCode('')
    setResults(null)
    toast.info('Converter reset. Paste new Python code.')
  }

  return (
    <MainLayout title="Python to Quantum Converter" description="Convert and execute Python code as quantum circuits">
      <div className="space-y-4 md:space-y-6">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center border border-hairline bg-surface-1">
                  <Code className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <CardTitle>Single-Step Conversion</CardTitle>
                  <CardDescription>Paste Python code, click once, get full results</CardDescription>
                </div>
              </div>

              <div className="flex gap-2">
                {results && (
                  <Button variant="outline" onClick={resetConverter}>
                    New Conversion
                  </Button>
                )}
                <Button onClick={executeFullFlow} disabled={!inputCode.trim() || isLoading} size="lg" className="min-w-[180px]">
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Running Full Flow...
                    </>
                  ) : (
                    <>
                      <Play className="mr-2 h-4 w-4" />
                      Convert & Execute
                    </>
                  )}
                </Button>
              </div>
            </div>
          </CardHeader>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
          <Card className="flex flex-col">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Code className="h-5 w-5 text-primary" />
                <CardTitle>Python Code Input</CardTitle>
              </div>
              <CardDescription>Paste your Python code (logic gates, functions, algorithms)</CardDescription>
            </CardHeader>
            <CardContent className="flex-1 p-0">
              <Textarea
                value={inputCode}
                onChange={(e) => setInputCode(e.target.value)}
                placeholder="# Paste your Python code here..."
                className="min-h-[500px] border-0 rounded-none font-mono text-sm resize-none"
                disabled={isLoading}
              />
            </CardContent>
          </Card>

          <Card className="flex flex-col">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Zap className="h-5 w-5 text-quantum" />
                  <CardTitle>Results</CardTitle>
                </div>
                {results && (
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => copyToClipboard(results.quantumCode, 'Quantum code')}>
                      {copied ? (
                        <>
                          <Check className="mr-2 h-4 w-4" />
                          Copied
                        </>
                      ) : (
                        <>
                          <Copy className="mr-2 h-4 w-4" />
                          Copy Code
                        </>
                      )}
                    </Button>
                    <Button size="sm" onClick={viewDetailedAnalysis}>
                      <Eye className="mr-2 h-4 w-4" />
                      Details
                    </Button>
                  </div>
                )}
              </div>
              <CardDescription>{results ? 'Conversion and execution results' : 'Results will appear here'}</CardDescription>
            </CardHeader>
            <CardContent className="flex-1 p-4">
              {isLoading ? (
                <div className="flex flex-col items-center justify-center h-[500px] space-y-4">
                  <Loader2 className="h-12 w-12 animate-spin text-quantum" />
                  <div className="text-center space-y-2">
                    <p className="font-medium text-ink">Running Full Conversion Flow...</p>
                    <div className="space-y-1 text-sm text-ink-muted">
                      <p>✓ 1. Translating Python to quantum code</p>
                      <p>✓ 2. Executing quantum circuit </p>
                      <p>→ 3. Analyzing results and performance</p>
                    </div>
                    <p className="text-xs text-ink-muted mt-4">This may take a few seconds...</p>
                  </div>
                </div>
              ) : results ? (
                <div className="space-y-6 h-[500px] overflow-y-auto pr-2">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Zap className="h-4 w-4 text-quantum" />
                      <h3 className="font-medium text-ink">Generated Quantum Code</h3>
                    </div>
                    <pre className="text-xs font-mono bg-surface-1 border border-hairline p-3 overflow-auto max-h-[150px] text-ink">
                      <code>{results.quantumCode}</code>
                    </pre>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <BarChart className="h-4 w-4 text-quantum" />
                      <h3 className="font-medium text-ink">Execution Summary</h3>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-3 bg-surface-1 border border-hairline">
                        <div className="text-sm text-ink-muted">Total Shots</div>
                        <div className="text-2xl font-semibold text-ink">1,000</div>
                      </div>
                      <div className="p-3 bg-surface-1 border border-hairline">
                        <div className="text-sm text-ink-muted">Circuit Depth</div>
                        <div className="text-2xl font-semibold text-ink">{results.executionResults.performance?.depth ?? 'N/A'}</div>
                      </div>
                      <div className="p-3 bg-surface-1 border border-hairline">
                        <div className="text-sm text-ink-muted">Qubits</div>
                        <div className="text-2xl font-semibold text-ink">{results.executionResults.performance?.num_qubits ?? 'N/A'}</div>
                      </div>
                      <div className="p-3 bg-surface-1 border border-hairline">
                        <div className="text-sm text-ink-muted">Execution Time</div>
                        <div className="text-lg font-semibold text-ink">
                          {results.executionResults.performance?.execution_time_seconds
                            ? `${(results.executionResults.performance.execution_time_seconds * 1000).toFixed(1)} ms`
                            : 'N/A'}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <h3 className="font-medium flex items-center gap-2 text-ink">
                        <BarChart className="h-4 w-4" />
                        Measurement Results
                      </h3>
                      <span className="text-sm text-ink-muted">
                        {Object.keys((results.executionResults as any).counts || {}).length} states
                      </span>
                    </div>
                    <div className="space-y-2">
                      {Object.entries((results.executionResults as any).counts || {}).map(([state, count]: [string, any]) => {
                        const probability = count / 1000
                        return (
                          <div key={state} className="space-y-1">
                            <div className="flex justify-between text-sm text-ink">
                              <span className="font-mono">|{state}⟩</span>
                              <span>
                                {count} shots ({(probability * 100).toFixed(1)}%)
                              </span>
                            </div>
                            <div className="h-2 bg-surface-2 overflow-hidden">
                              <div className="h-full bg-quantum transition-all duration-500" style={{ width: `${probability * 100}%` }} />
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>

                  <div className="flex gap-2 pt-4 border-t border-hairline">
                    <Button variant="outline" className="flex-1" onClick={exportResults}>
                      <Download className="mr-2 h-4 w-4" />
                      Export JSON
                    </Button>
                    <Button className="flex-1" onClick={viewDetailedAnalysis}>
                      <Eye className="mr-2 h-4 w-4" />
                      View Full Analysis
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-[500px] text-center space-y-6">
                  <div className="space-y-3">
                    <div className="mx-auto flex h-16 w-16 items-center justify-center bg-quantum/10">
                      <Zap className="h-8 w-8 text-quantum" />
                    </div>
                    <div>
                      <p className="font-medium text-ink">Ready to Convert</p>
                      <p className="text-sm text-ink-muted">Paste Python code and click "Convert & Execute"</p>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  )
}
