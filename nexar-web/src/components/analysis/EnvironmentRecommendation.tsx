/**
 * Environment Recommendation Component
 * Takes code analysis results and gets hardware recommendations from the decision engine
 */

import { useState } from 'react'
import { Cpu, DollarSign, Clock, Loader2, AlertCircle, CheckCircle2, Gauge, Lightbulb, Sparkles, GitBranch } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Separator } from '@/components/ui/separator'
import { ConfidenceRing } from '@/components/ui/ConfidenceRing'
import { FadeIn } from '@/components/ui/FadeIn'
import { formatDurationMs } from '@/lib/number-format'
import { decisionEngineService } from '@/services/decision-engine-service'
import type { AnalysisResult } from '@/types/codeAnalysis'
import { ProblemType, TimeComplexity, HardwareType, type CodeAnalysisInput, type DecisionEngineResponse } from '@/types/decision-engine.tp'

interface EnvironmentRecommendationProps {
  analysisResult: AnalysisResult
}

function mapProblemType(type: string): ProblemType {
  const mapping: Record<string, ProblemType> = {
    search: ProblemType.SEARCH,
    optimization: ProblemType.OPTIMIZATION,
    simulation: ProblemType.SIMULATION,
    machine_learning: ProblemType.MATRIX_OPS,
    factorization: ProblemType.FACTORIZATION,
    cryptography: ProblemType.FACTORIZATION,
    sampling: ProblemType.RANDOM_CIRCUIT,
    classical: ProblemType.SORTING,
    unknown: ProblemType.OPTIMIZATION,
  }
  return mapping[type] || ProblemType.OPTIMIZATION
}

function mapTimeComplexity(complexity: string): TimeComplexity {
  const mapping: Record<string, TimeComplexity> = {
    'O(1)': TimeComplexity.POLYNOMIAL,
    'O(log n)': TimeComplexity.POLYNOMIAL,
    'O(n)': TimeComplexity.POLYNOMIAL,
    'O(n log n)': TimeComplexity.NLOGN,
    'O(n^2)': TimeComplexity.POLYNOMIAL,
    'O(n^3)': TimeComplexity.POLYNOMIAL,
    'O(2^n)': TimeComplexity.EXPONENTIAL,
    'O(n!)': TimeComplexity.EXPONENTIAL,
    'O(n^k)': TimeComplexity.POLYNOMIAL,
    'O(sqrt(n))': TimeComplexity.QUADRATIC_SPEEDUP,
    unknown: TimeComplexity.POLYNOMIAL,
  }
  return mapping[complexity] || TimeComplexity.POLYNOMIAL
}

export function EnvironmentRecommendation({ analysisResult }: EnvironmentRecommendationProps) {
  const [budgetLimit, setBudgetLimit] = useState<string>('10.00')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [recommendation, setRecommendation] = useState<DecisionEngineResponse | null>(null)

  const handleGetRecommendation = async () => {
    setIsLoading(true)
    setError(null)

    const input: CodeAnalysisInput = {
      problem_type: mapProblemType(analysisResult.problem_type),
      problem_size: analysisResult.problem_size,
      qubits_required: analysisResult.qubits_required,
      circuit_depth: analysisResult.circuit_depth,
      gate_count: analysisResult.gate_count,
      cx_gate_ratio: analysisResult.cx_gate_ratio,
      superposition_score: analysisResult.superposition_score,
      entanglement_score: analysisResult.entanglement_score,
      time_complexity: mapTimeComplexity(analysisResult.time_complexity),
      memory_requirement_mb: analysisResult.memory_requirement_mb,
    }

    try {
      const budget = parseFloat(budgetLimit) || undefined
      const result = await decisionEngineService.predict(input, budget)
      setRecommendation(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get recommendation')
    } finally {
      setIsLoading(false)
    }
  }

  const getHardwareBadgeVariant = (hardware: HardwareType | string) => {
    if (hardware === HardwareType.QUANTUM || hardware === 'Quantum') return 'quantum' as const
    if (hardware === HardwareType.CLASSICAL || hardware === 'Classical') return 'classical' as const
    return 'hybrid' as const
  }

  return (
    <div className="space-y-4">
      <Separator />

      <Card variant="glass">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cpu className="h-5 w-5 text-primary" />
            Environment Recommendation
          </CardTitle>
          <CardDescription>Get an AI-powered hardware recommendation based on your code analysis</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
            <div className="flex-1">
              <Label className="text-sm text-ink-muted">Budget Limit (USD)</Label>
              <div className="relative mt-1">
                <DollarSign className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-subtle" />
                <Input
                  type="number"
                  step="0.01"
                  min="0"
                  value={budgetLimit}
                  onChange={(e) => setBudgetLimit(e.target.value)}
                  placeholder="10.00"
                  className="pl-9"
                />
              </div>
              <p className="mt-1 text-xs text-ink-muted">Optional: Set a maximum cost per execution</p>
            </div>
            <Button variant="quantum" onClick={handleGetRecommendation} disabled={isLoading} className="gap-2">
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  Get Recommendation
                </>
              )}
            </Button>
          </div>

          <div className="mt-4 border border-hairline bg-surface-1 p-3">
            <p className="text-xs font-medium text-ink-muted mb-2">Analysis Parameters</p>
            <div className="grid grid-cols-2 gap-2 text-xs sm:grid-cols-3 md:grid-cols-5">
              <div>
                <span className="text-ink-muted">Problem: </span>
                <span className="font-mono text-ink">{analysisResult.problem_type}</span>
              </div>
              <div>
                <span className="text-ink-muted">Size: </span>
                <span className="font-mono text-ink">{analysisResult.problem_size}</span>
              </div>
              <div>
                <span className="text-ink-muted">Qubits: </span>
                <span className="font-mono text-ink">{analysisResult.qubits_required}</span>
              </div>
              <div>
                <span className="text-ink-muted">Depth: </span>
                <span className="font-mono text-ink">{analysisResult.circuit_depth}</span>
              </div>
              <div>
                <span className="text-ink-muted">Memory: </span>
                <span className="font-mono text-ink">{analysisResult.memory_requirement_mb.toFixed(2)}MB</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {recommendation && recommendation.recommendation && (
        <FadeIn className="space-y-4">
          <Card variant={recommendation.recommendation.recommended_hardware === HardwareType.QUANTUM ? 'quantum' : 'glass'}>
            <CardHeader>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 text-success" />
                  Hardware Recommendation
                </CardTitle>
                <Badge variant={getHardwareBadgeVariant(recommendation.recommendation.recommended_hardware)} className="w-fit">
                  {recommendation.recommendation.recommended_hardware} Execution
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <div className="text-center">
                  <ConfidenceRing
                    value={Math.round(recommendation.recommendation.confidence * 100)}
                    size={80}
                    variant={recommendation.recommendation.recommended_hardware === HardwareType.QUANTUM ? 'quantum' : 'classical'}
                    className="mx-auto"
                  />
                  <p className="mt-1 text-xs text-ink-muted">Confidence</p>
                </div>

                <div className="flex flex-col justify-center border border-hairline bg-surface-1 p-3">
                  <div className="flex items-center gap-2 text-ink-muted">
                    <Clock className="h-4 w-4" />
                    <span className="text-xs">Est. Execution Time</span>
                  </div>
                  <p className="mt-1 font-mono text-xl font-semibold text-ink">
                    {formatDurationMs(recommendation.estimated_execution_time_ms)}
                  </p>
                </div>

                <div className="flex flex-col justify-center border border-hairline bg-surface-1 p-3">
                  <div className="flex items-center gap-2 text-ink-muted">
                    <DollarSign className="h-4 w-4" />
                    <span className="text-xs">Est. Cost</span>
                  </div>
                  <p className="mt-1 font-mono text-xl font-semibold text-success">
                    ${recommendation.estimated_cost_usd?.toFixed(4) || 'N/A'}
                  </p>
                </div>

                <div className="flex flex-col justify-center border border-hairline bg-surface-1 p-3">
                  <div className="flex items-center gap-2 text-ink-muted">
                    <Gauge className="h-4 w-4" />
                    <span className="text-xs">Quantum Probability</span>
                  </div>
                  <p className="mt-1 font-mono text-xl font-semibold text-quantum">
                    {Math.round(recommendation.recommendation.quantum_probability * 100)}%
                  </p>
                  <p className="text-xs text-ink-muted">Classical: {Math.round(recommendation.recommendation.classical_probability * 100)}%</p>
                </div>
              </div>

              <div className="mt-4 border border-hairline bg-surface-1 p-4">
                <div className="flex items-center gap-2 text-sm font-semibold text-ink">
                  <Lightbulb className="h-4 w-4 text-ink" />
                  Decision Rationale
                </div>
                <p className="mt-2 text-sm text-ink-muted leading-relaxed">{recommendation.recommendation.rationale}</p>
              </div>
            </CardContent>
          </Card>

          {recommendation.alternatives && recommendation.alternatives.length > 0 && (
            <Card variant="glass">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <GitBranch className="h-4 w-4 text-ink" />
                  Alternative Options
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  {recommendation.alternatives.map((alt, idx) => (
                    <div key={idx} className="border border-hairline bg-surface-1 p-4 transition-colors hover:bg-surface-2">
                      <div className="flex items-center justify-between">
                        <Badge variant={getHardwareBadgeVariant(alt.hardware)}>{alt.hardware}</Badge>
                        <span className="font-mono text-sm text-ink">{Math.round(alt.confidence * 100)}% confidence</span>
                      </div>
                      <p className="mt-2 text-xs text-ink-muted">{alt.trade_off}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </FadeIn>
      )}

      {recommendation && !recommendation.recommendation && recommendation.error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{recommendation.error}</AlertDescription>
        </Alert>
      )}
    </div>
  )
}
