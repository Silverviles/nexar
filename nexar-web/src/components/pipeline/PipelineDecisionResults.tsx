/**
 * Pipeline Decision Results
 * Displays the Decision Engine recommendation within the pipeline flow.
 */

import { useState } from 'react'
import { Award, Clock, DollarSign, Gauge, Brain, GitBranch, MessageSquare, ChevronDown, ChevronUp } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ConfidenceRing } from '@/components/ui/ConfidenceRing'
import { FadeIn } from '@/components/ui/FadeIn'
import { type DecisionEngineResponse, type CodeAnalysisInput, HardwareType } from '@/types/decision-engine.tp'
import { cn } from '@/lib/utils'
import { formatDurationMs } from '@/lib/number-format'

function formatCost(usd: number | null | undefined): string {
  if (usd == null) return 'N/A'
  if (usd > 1e12) return 'Infeasible'
  if (usd < 0.01) return `$${usd.toFixed(6)}`
  if (usd < 1000) return `$${usd.toFixed(2)}`
  if (usd < 1e6) return `$${(usd / 1000).toFixed(1)}K`
  if (usd < 1e9) return `$${(usd / 1e6).toFixed(1)}M`
  return `$${(usd / 1e9).toFixed(1)}B`
}

interface PipelineDecisionResultsProps {
  result: DecisionEngineResponse
  mappedInput: CodeAnalysisInput | null
}

export function PipelineDecisionResults({ result, mappedInput }: PipelineDecisionResultsProps) {
  const [showMappedInput, setShowMappedInput] = useState(false)

  if (!result.recommendation) {
    return (
      <FadeIn>
        <Card variant="glass">
          <CardContent className="py-6">
            <p className="text-sm text-ink-muted">
              Decision Engine did not return a recommendation.
              {result.error && ` Error: ${result.error}`}
            </p>
          </CardContent>
        </Card>
      </FadeIn>
    )
  }

  const { recommendation, alternatives, estimated_execution_time_ms, estimated_cost_usd } = result
  const isQuantum = recommendation.recommended_hardware === HardwareType.QUANTUM
  const confidencePercent = Math.round(recommendation.confidence * 100)

  const getBadgeVariant = (hardware: string) => {
    if (hardware === 'Quantum') return 'quantum' as const
    if (hardware === 'Classical') return 'classical' as const
    return 'hybrid' as const
  }

  return (
    <FadeIn className="space-y-4">
      <Card variant={isQuantum ? 'quantum' : 'glass'}>
        <CardHeader>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5" />
              Hardware Recommendation
            </CardTitle>
            <Badge variant={getBadgeVariant(recommendation.recommended_hardware)}>{recommendation.recommended_hardware} Execution</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="text-center">
              <ConfidenceRing value={confidencePercent} size={80} variant={isQuantum ? 'quantum' : 'classical'} className="mx-auto" />
              <p className="mt-1 text-xs text-ink-muted">Confidence</p>
            </div>

            <div className="flex flex-col justify-center">
              <div className="flex items-center gap-1.5 text-ink-muted">
                <Clock className="h-3.5 w-3.5" />
                <span className="text-xs">Expected Time</span>
              </div>
              <p className="mt-1 font-mono text-xl font-semibold text-ink">{formatDurationMs(estimated_execution_time_ms)}</p>
            </div>

            <div className="flex flex-col justify-center">
              <div className="flex items-center gap-1.5 text-ink-muted">
                <DollarSign className="h-3.5 w-3.5" />
                <span className="text-xs">Estimated Cost</span>
              </div>
              <p className="mt-1 font-mono text-xl font-semibold text-ink">{formatCost(estimated_cost_usd)}</p>
            </div>

            <div className="flex flex-col justify-center">
              <div className="flex items-center gap-1.5 text-ink-muted">
                <Gauge className="h-3.5 w-3.5" />
                <span className="text-xs">Quantum Prob.</span>
              </div>
              <p className={cn('mt-1 font-mono text-xl font-semibold', isQuantum ? 'text-quantum' : 'text-ink')}>
                {Math.round(recommendation.quantum_probability * 100)}%
              </p>
              <p className="text-xs text-ink-muted">Classical: {Math.round(recommendation.classical_probability * 100)}%</p>
            </div>
          </div>

          <div className="mt-4 border border-hairline bg-surface-1 p-3">
            <div className="flex items-center gap-2 mb-2">
              <MessageSquare className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium text-ink">Rationale</span>
            </div>
            <p className="text-sm text-ink-muted leading-relaxed">{recommendation.rationale}</p>
          </div>
        </CardContent>
      </Card>

      {alternatives && alternatives.length > 0 && (
        <Card variant="glass">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <GitBranch className="h-4 w-4 text-ink" />
              Alternatives
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {alternatives.map((alt, idx) => (
                <div key={idx} className="flex items-center justify-between border border-hairline bg-surface-1 p-3">
                  <div className="flex items-center gap-3">
                    <Badge variant={getBadgeVariant(alt.hardware)}>{alt.hardware}</Badge>
                    <span className="text-xs text-ink-muted">{alt.trade_off}</span>
                  </div>
                  <span className="font-mono text-sm text-ink">{(alt.confidence * 100).toFixed(0)}%</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {mappedInput && (
        <div className="border border-hairline bg-surface-1 p-3">
          <button
            onClick={() => setShowMappedInput(!showMappedInput)}
            className="flex w-full items-center justify-between text-xs text-ink-muted hover:text-ink transition-colors"
          >
            <span className="flex items-center gap-1.5">
              <Brain className="h-3.5 w-3.5" />
              View mapped parameters sent to Decision Engine
            </span>
            {showMappedInput ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
          </button>
          {showMappedInput && (
            <pre className="mt-2 overflow-x-auto bg-canvas border border-hairline p-3 text-xs font-mono text-ink">
              {JSON.stringify(mappedInput, null, 2)}
            </pre>
          )}
        </div>
      )}
    </FadeIn>
  )
}
