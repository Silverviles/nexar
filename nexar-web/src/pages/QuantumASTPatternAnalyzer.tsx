import { useState } from 'react'
import { Loader2, Code, Zap, BarChart, Search, Target, Gauge, Sparkles, AlertCircle, Layers, Brain } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { MainLayout } from '@/components/layout/MainLayout'
import { toast } from 'sonner'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import type { AnalysisResponse } from '@/types/code-converstion.tp'
import quantumAnalysisService from '@/services/quantumAnalysisService'

const suitabilityBadge: Record<string, string> = {
  high: 'border-success/40 bg-success/10 text-success',
  medium: 'border-warning/50 bg-warning/15 text-ink',
  low: 'border-error/40 bg-error/10 text-error',
}

const confidenceColor = (confidence: number) => {
  if (confidence >= 0.8) return 'text-success'
  if (confidence >= 0.6) return 'text-ink'
  return 'text-error'
}

export default function QuantumPatternAnalyzer() {
  const [inputCode, setInputCode] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<AnalysisResponse | null>(null)
  const [includeCode, setIncludeCode] = useState(false)

  const analyzeCode = async () => {
    if (!inputCode.trim() || isLoading) return

    setIsLoading(true)
    setResults(null)

    try {
      const data = await quantumAnalysisService.analyzeCode(inputCode, includeCode)
      setResults(data)
    } catch (error) {
      console.error('Analysis error:', error)
      // Error is already handled in the service
    } finally {
      setIsLoading(false)
    }
  }

  const resetAnalyzer = () => {
    setInputCode('')
    setResults(null)
    setIncludeCode(false)
    toast.info('Analyzer reset. Paste new Python code.')
  }

  return (
    <MainLayout title="Quantum Pattern Analyzer" description="Analyze Python code for quantum suitability and detect quantum-amenable patterns">
      <div className="space-y-4 md:space-y-6">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center border border-hairline bg-surface-1">
                  <Brain className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <CardTitle>Quantum Pattern Recognition</CardTitle>
                  <CardDescription>Detect quantum-amenable algorithms and estimate quantum advantage</CardDescription>
                </div>
              </div>

              <div className="flex gap-2">
                {results && (
                  <Button variant="outline" onClick={resetAnalyzer}>
                    New Analysis
                  </Button>
                )}
                <Button onClick={analyzeCode} disabled={!inputCode.trim() || isLoading} size="lg" className="min-w-[180px]" variant="quantum">
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Target className="mr-2 h-4 w-4" />
                      Analyze Code
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
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Code className="h-5 w-5 text-primary" />
                  <CardTitle>Python Code Input</CardTitle>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="include-code"
                    checked={includeCode}
                    onChange={(e) => setIncludeCode(e.target.checked)}
                    className="h-4 w-4"
                  />
                  <label htmlFor="include-code" className="text-sm text-ink-muted">
                    Include code in results
                  </label>
                </div>
              </div>
              <CardDescription>Paste Python algorithms to analyze quantum suitability</CardDescription>
            </CardHeader>
            <CardContent className="flex-1 p-0">
              <Textarea
                value={inputCode}
                onChange={(e) => setInputCode(e.target.value)}
                placeholder={'# Paste your Python algorithm here...\n# Example: Search algorithms, optimization problems, etc.\n\ndef search(arr, target):\n    for i in range(len(arr)):\n        if arr[i] == target:\n            return i\n    return -1'}
                className="min-h-[500px] border-0 rounded-none font-mono text-sm resize-none"
                disabled={isLoading}
              />
            </CardContent>
          </Card>

          <Card className="flex flex-col">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary" />
                <CardTitle>Analysis Results</CardTitle>
              </div>
              <CardDescription>{results ? 'Quantum pattern analysis results' : 'Results will appear here'}</CardDescription>
            </CardHeader>
            <CardContent className="flex-1 p-4">
              {isLoading ? (
                <div className="flex flex-col items-center justify-center h-[500px] space-y-4">
                  <Loader2 className="h-12 w-12 animate-spin text-primary" />
                  <div className="text-center space-y-2">
                    <p className="font-medium text-ink">Analyzing Quantum Patterns...</p>
                    <div className="space-y-1 text-sm text-ink-muted">
                      <p>✓ 1. Parsing Python AST</p>
                      <p>✓ 2. Detecting algorithm patterns</p>
                      <p>→ 3. Calculating quantum suitability</p>
                      <p>→ 4. Generating recommendations</p>
                    </div>
                    <p className="text-xs text-ink-muted mt-4">Analyzing code structure and patterns...</p>
                  </div>
                </div>
              ) : results ? (
                <div className="space-y-6 h-[500px] overflow-y-auto pr-2">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Gauge className="h-5 w-5 text-primary" />
                        <h3 className="font-medium text-ink">Quantum Suitability</h3>
                      </div>
                      <Badge variant="outline" className={`px-3 py-1 ${suitabilityBadge[results.quantum_suitability.level]}`}>
                        {results.quantum_suitability.level.toUpperCase()}
                      </Badge>
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between text-sm text-ink">
                        <span>Suitability Score</span>
                        <span className="font-semibold">{results.quantum_suitability.score.toFixed(3)}</span>
                      </div>
                      <Progress value={results.quantum_suitability.score * 100} className="h-2" />
                      <p className="text-sm text-ink-muted">{results.quantum_suitability.message}</p>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <Layers className="h-5 w-5 text-primary" />
                      <h3 className="font-medium text-ink">Detected Patterns</h3>
                      <Badge variant="outline" className="ml-auto">
                        {results.patterns.length} patterns
                      </Badge>
                    </div>

                    {results.patterns.length > 0 ? (
                      <div className="space-y-3">
                        {results.patterns.map((pattern, index) => (
                          <Card key={index} className="border border-hairline">
                            <CardContent className="p-4">
                              <div className="flex items-start justify-between mb-2">
                                <div className="space-y-1">
                                  <div className="flex items-center gap-2">
                                    <h4 className="font-medium capitalize text-ink">{pattern.pattern.replace(/_/g, ' ')}</h4>
                                    <Badge variant="secondary" className={`text-xs ${confidenceColor(pattern.confidence)}`}>
                                      {Math.round(pattern.confidence * 100)}% confident
                                    </Badge>
                                  </div>
                                  <h4 className="font-medium capitalize text-ink">{pattern.quantum_algo}</h4>
                                </div>
                              </div>

                              <div className="grid grid-cols-2 gap-2 mt-3 text-sm">
                                <div className="flex items-center gap-1">
                                  <Sparkles className="h-3 w-3 text-ink-muted" />
                                  <span className="text-ink-muted">Score:</span>
                                  <span className="font-medium ml-1 text-ink">{pattern.suitability_score.toFixed(2)}</span>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    ) : (
                      <div className="p-4 text-center border border-hairline bg-surface-1">
                        <AlertCircle className="h-8 w-8 text-ink-muted mx-auto mb-2" />
                        <p className="text-sm text-ink-muted">No quantum-amenable patterns detected in this code</p>
                      </div>
                    )}
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <BarChart className="h-5 w-5 text-primary" />
                      <h3 className="font-medium text-ink">Code Metrics</h3>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      <div className="p-3 bg-surface-1 border border-hairline">
                        <div className="text-sm text-ink-muted">Lines</div>
                        <div className="text-2xl font-semibold text-ink">{results.metrics.line_count}</div>
                      </div>
                      <div className="p-3 bg-surface-1 border border-hairline">
                        <div className="text-sm text-ink-muted">Functions</div>
                        <div className="text-2xl font-semibold text-ink">{results.metrics.function_count}</div>
                      </div>
                      <div className="p-3 bg-surface-1 border border-hairline">
                        <div className="text-sm text-ink-muted">Loops</div>
                        <div className="text-2xl font-semibold text-ink">{results.metrics.loop_count}</div>
                      </div>
                      <div className="p-3 bg-surface-1 border border-hairline">
                        <div className="text-sm text-ink-muted">Conditions</div>
                        <div className="text-2xl font-semibold text-ink">{results.metrics.condition_count}</div>
                      </div>
                      <div className="p-3 bg-surface-1 border border-hairline">
                        <div className="text-sm text-ink-muted">Has Functions</div>
                        <div className="text-lg font-semibold text-ink">{results.metrics.has_function ? '✓' : '✗'}</div>
                      </div>
                      <div className="p-3 bg-surface-1 border border-hairline">
                        <div className="text-sm text-ink-muted">Has Loops</div>
                        <div className="text-lg font-semibold text-ink">{results.metrics.has_loop ? '✓' : '✗'}</div>
                      </div>
                    </div>
                  </div>

                  {results.quantum_suitability.level === 'high' && (
                    <div className="p-4 border border-primary/30 bg-primary/5">
                      <div className="flex items-center gap-2 mb-2">
                        <Zap className="h-4 w-4 text-primary" />
                        <h3 className="font-medium text-ink">Quantum Opportunity</h3>
                      </div>
                      <p className="text-sm mb-3 text-ink-muted">This code is highly suitable for quantum conversion. Consider:</p>
                      <ul className="space-y-1 text-sm">
                        {results.patterns.map((pattern, index) => (
                          <li key={index} className="flex items-start gap-2 text-ink">
                            <div className="h-1.5 w-1.5 rounded-full bg-primary mt-1.5 flex-shrink-0" />
                            <span>
                              Convert to <span className="font-medium">{pattern.quantum_algo}</span>
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-[500px] text-center space-y-6">
                  <div className="space-y-3">
                    <div className="mx-auto flex h-16 w-16 items-center justify-center bg-surface-1">
                      <Search className="h-8 w-8 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium text-ink">Ready to Analyze</p>
                      <p className="text-sm text-ink-muted">Paste Python code and click "Analyze Code"</p>
                    </div>
                  </div>

                  <div className="p-3 bg-surface-1 border border-hairline text-left">
                    <div className="flex items-center gap-2 mb-1">
                      <Target className="h-4 w-4 text-primary" />
                      <span className="text-sm font-medium text-ink">What we detect:</span>
                    </div>
                    <ul className="text-xs text-ink-muted space-y-1">
                      <li>• Linear/Binary Search algorithms</li>
                      <li>• Coin Flip</li>
                      <li>• Hidden Bit String</li>
                      <li>• Parity checking</li>
                      <li>• Swap</li>
                    </ul>
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
