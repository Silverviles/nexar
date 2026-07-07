/**
 * Analysis Results Display Component
 */

import { useState, useEffect } from 'react'
import { CheckCircle, Cpu, Code, BarChart3, Terminal } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { FadeIn } from '@/components/ui/FadeIn'
import { ConfidenceRing } from '@/components/ui/ConfidenceRing'
import { ClassicalMetricsDisplay } from './ClassicalMetrics'
import { QuantumMetricsDisplay } from './QuantumMetrics'
import { EnvironmentRecommendation } from './EnvironmentRecommendation'
import { CodeQualityScore } from './CodeQualityScore'
import { OptimizationSuggestions } from './OptimizationSuggestions'
import { ASTTreeViewer } from './ASTTreeViewer'
import { ComplexityHeatmap } from './ComplexityHeatmap'
import type { AnalysisResult } from '@/types/codeAnalysis'
import { getLanguageDisplayName } from '@/lib/languageDetection'

interface ResultsDisplayProps {
  result: AnalysisResult
}

export function ResultsDisplay({ result }: ResultsDisplayProps) {
  const [terminalText, setTerminalText] = useState('')
  const isQuantum = result.is_quantum

  /* Character-stepping typewriter effect -- kept as the original setInterval logic
     since framer-motion has no native text-stepping primitive worth swapping in for this. */
  useEffect(() => {
    if (!result.analysis_notes) return

    setTerminalText('')
    let index = 0
    const text = result.analysis_notes

    const interval = setInterval(() => {
      index++
      if (index <= text.length) {
        setTerminalText(text.slice(0, index))
      } else {
        clearInterval(interval)
      }
    }, 20)

    return () => clearInterval(interval)
  }, [result.analysis_notes])

  return (
    <FadeIn className="space-y-6">
      <Card variant={isQuantum ? 'quantum' : 'glass'}>
        <CardHeader>
          <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
            <div className="text-center sm:text-left">
              <CardTitle className="flex items-center justify-center gap-2 sm:justify-start">
                <CheckCircle className="h-6 w-6 text-success" />
                Analysis Complete
              </CardTitle>
              <p className="mt-2 text-sm text-ink-muted">
                Language: {getLanguageDisplayName(result.detected_language)} • Confidence: {(result.confidence_score * 100).toFixed(1)}%
              </p>
            </div>

            <ConfidenceRing value={result.confidence_score * 100} size={96} variant={isQuantum ? 'quantum' : 'classical'} />
          </div>
        </CardHeader>

        <CardContent>
          <div className="space-y-3">
            <div className="border border-hairline bg-surface-1 p-4">
              <div className="flex items-center gap-2">
                {isQuantum ? <Cpu className="h-5 w-5 text-quantum" /> : <Code className="h-5 w-5 text-classical" />}
                <span className="text-lg font-semibold text-ink">
                  {isQuantum ? 'QUANTUM CODE DETECTED — HARDWARE RECOMMENDATION PENDING' : 'CLASSICAL CODE DETECTED — HARDWARE RECOMMENDATION PENDING'}
                </span>
              </div>
              <p className="mt-2 text-sm text-ink-muted">
                Problem Type: {result.problem_type.toUpperCase()} • Size: {result.problem_size} • Complexity: {result.time_complexity}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
              <div className="border border-hairline bg-surface-1 p-3">
                <div className="text-xs text-ink-muted">Memory</div>
                <div className="mt-1 font-mono text-sm font-semibold text-ink">{result.memory_requirement_mb.toFixed(3)} MB</div>
              </div>

              {isQuantum && (
                <>
                  <div className="border border-hairline bg-surface-1 p-3">
                    <div className="text-xs text-ink-muted">Qubits</div>
                    <div className="mt-1 font-mono text-sm font-semibold text-ink">{result.qubits_required}</div>
                  </div>
                  <div className="border border-hairline bg-surface-1 p-3">
                    <div className="text-xs text-ink-muted">Circuit Depth</div>
                    <div className="mt-1 font-mono text-sm font-semibold text-ink">{result.circuit_depth}</div>
                  </div>
                  <div className="border border-hairline bg-surface-1 p-3">
                    <div className="text-xs text-ink-muted">Gates</div>
                    <div className="mt-1 font-mono text-sm font-semibold text-ink">{result.gate_count}</div>
                  </div>
                </>
              )}

              {!isQuantum && result.classical_metrics && (
                <>
                  <div className="border border-hairline bg-surface-1 p-3">
                    <div className="text-xs text-ink-muted">Cyclomatic (Sum/Max)</div>
                    <div className="mt-1 font-mono text-sm font-semibold text-ink">
                      {result.classical_metrics.cyclomatic_complexity}/{result.classical_metrics.cyclomatic_complexity_max}
                    </div>
                  </div>
                  <div className="border border-hairline bg-surface-1 p-3">
                    <div className="text-xs text-ink-muted">LOC</div>
                    <div className="mt-1 font-mono text-sm font-semibold text-ink">{result.classical_metrics.lines_of_code}</div>
                  </div>
                  <div className="border border-hairline bg-surface-1 p-3">
                    <div className="text-xs text-ink-muted">Functions</div>
                    <div className="mt-1 font-mono text-sm font-semibold text-ink">{result.classical_metrics.function_count}</div>
                  </div>
                </>
              )}
            </div>

            {result.detected_algorithms.length > 0 && (
              <div className="border border-quantum/30 bg-quantum/5 p-4">
                <div className="flex items-center gap-2 text-sm font-semibold text-quantum">
                  <BarChart3 className="h-4 w-4" />
                  Detected Algorithms
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {result.detected_algorithms.map((algo) => (
                    <Badge key={algo} variant="quantum">
                      {algo.replace(/_/g, ' ').toUpperCase()}
                    </Badge>
                  ))}
                  {result.algorithm_detection_source && (
                    <Badge variant="outline" className="text-xs opacity-70">
                      {result.algorithm_detection_source}
                    </Badge>
                  )}
                </div>
              </div>
            )}

            {result.recursion && (
              <div className="border border-success/30 bg-success/5 p-4">
                <div className="flex items-center gap-2 text-sm font-semibold text-success">
                  <Terminal className="h-4 w-4" />
                  Recursion Analysis
                </div>
                <div className="mt-3 grid gap-3 sm:grid-cols-2">
                  <div className="border border-hairline bg-surface-1 p-3">
                    <div className="text-xs text-ink-muted">Has Recursion</div>
                    <div className="mt-1 font-mono text-sm font-semibold text-ink">{result.recursion.has_recursion ? 'Yes' : 'No'}</div>
                  </div>
                  <div className="border border-hairline bg-surface-1 p-3">
                    <div className="text-xs text-ink-muted">Recursive Functions</div>
                    <div className="mt-1 font-mono text-sm font-semibold text-ink">
                      {result.recursion.recursive_functions.length > 0 ? result.recursion.recursive_functions.join(', ') : 'None'}
                    </div>
                  </div>
                  <div className="border border-hairline bg-surface-1 p-3">
                    <div className="text-xs text-ink-muted">Recursion Patterns</div>
                    <div className="mt-1 font-mono text-xs font-semibold text-ink">
                      {Object.keys(result.recursion.recursion_patterns).length > 0
                        ? Object.entries(result.recursion.recursion_patterns)
                            .map(([name, pattern]) => `${name}: ${pattern}`)
                            .join(' • ')
                        : 'None'}
                    </div>
                  </div>
                  <div className="border border-hairline bg-surface-1 p-3">
                    <div className="text-xs text-ink-muted">Recursion Depths</div>
                    <div className="mt-1 font-mono text-xs font-semibold text-ink">
                      {Object.keys(result.recursion.recursion_depths).length > 0
                        ? Object.entries(result.recursion.recursion_depths)
                            .map(([name, count]) => `${name}: ${count}`)
                            .join(' • ')
                        : 'None'}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Separator />

      {result.quantum_metrics && <QuantumMetricsDisplay metrics={result.quantum_metrics} detectedAlgorithms={result.detected_algorithms} />}

      {result.classical_metrics && <ClassicalMetricsDisplay metrics={result.classical_metrics} problemSize={result.problem_size} />}

      <Card variant="glass">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base font-mono text-ink">
            <Terminal className="h-4 w-4" />
            Analysis Log
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-surface-1 border border-hairline p-4 font-mono text-xs">
            <div className="flex items-start gap-2">
              <span className="text-success">$</span>
              <div className="flex-1">
                <p className="text-ink">{terminalText}</p>
                <span className="inline-block h-4 w-2 animate-pulse bg-success" />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Separator />

      {result.code_quality_metrics && <CodeQualityScore metrics={result.code_quality_metrics} />}

      <ComplexityHeatmap classicalMetrics={result.classical_metrics} quantumMetrics={result.quantum_metrics} isQuantum={result.is_quantum} />

      {result.optimization_suggestions && result.optimization_suggestions.length > 0 && (
        <OptimizationSuggestions suggestions={result.optimization_suggestions} />
      )}

      {result.ast_structure && <ASTTreeViewer ast={result.ast_structure} />}

      <Separator />

      <EnvironmentRecommendation analysisResult={result} />
    </FadeIn>
  )
}
