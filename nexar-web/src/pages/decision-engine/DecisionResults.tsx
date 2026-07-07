import { useLocation, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { Award, Clock, DollarSign, Gauge, Brain, GitBranch, MessageSquare, ArrowLeft } from 'lucide-react'
import { MainLayout } from '@/components/layout/MainLayout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ConfidenceRing } from '@/components/ui/ConfidenceRing'
import { FadeIn } from '@/components/ui/FadeIn'
import { formatDurationMs } from '@/lib/number-format'
import { type DecisionEngineResponse, HardwareType } from '@/types/decision-engine.tp'

function formatCost(usd: number | null | undefined): string {
  if (usd == null) return 'N/A'
  if (usd > 1e12) return 'Infeasible'
  if (usd < 0.01) return `$${usd.toFixed(6)}`
  if (usd < 1000) return `$${usd.toFixed(2)}`
  if (usd < 1e6) return `$${(usd / 1000).toFixed(1)}K`
  if (usd < 1e9) return `$${(usd / 1e6).toFixed(1)}M`
  return `$${(usd / 1e9).toFixed(1)}B`
}

export default function DecisionResults() {
  const location = useLocation()
  const navigate = useNavigate()
  const [result, setResult] = useState<DecisionEngineResponse | null>(null)

  useEffect(() => {
    const state = location.state as { result?: DecisionEngineResponse } | null
    if (state?.result) {
      setResult(state.result)
    } else {
      navigate('/decision-engine')
    }
  }, [location, navigate])

  if (!result || !result.recommendation) {
    return (
      <MainLayout title="Decision Results" description="Hardware recommendation results">
        <Alert>
          <AlertDescription>No decision data available. Please submit a decision request first.</AlertDescription>
        </Alert>
        <Button onClick={() => navigate('/decision-engine')} className="mt-4">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Decision Engine
        </Button>
      </MainLayout>
    )
  }

  const { recommendation, alternatives, estimated_execution_time_ms, estimated_cost_usd } = result
  const isQuantum = recommendation.recommended_hardware === HardwareType.QUANTUM
  const isClassical = recommendation.recommended_hardware === HardwareType.CLASSICAL

  const getBadgeVariant = () => {
    if (isQuantum) return 'quantum' as const
    if (isClassical) return 'classical' as const
    return 'hybrid' as const
  }

  const confidencePercent = Math.round(recommendation.confidence * 100)

  return (
    <MainLayout title="Decision Results" description="Comprehensive routing recommendation">
      <div className="space-y-4 md:space-y-6">
        <Button variant="outline" onClick={() => navigate('/decision-engine')}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          New Decision
        </Button>

        <FadeIn scale>
          <Card variant={isQuantum ? 'quantum' : 'glass'}>
            <CardHeader>
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Award className="h-5 w-5" />
                  Primary Recommendation
                </CardTitle>
                <Badge variant={getBadgeVariant()}>{recommendation.recommended_hardware} Execution</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:gap-6 lg:grid-cols-4">
                <div className="text-center">
                  <ConfidenceRing
                    value={confidencePercent}
                    size={96}
                    variant={isQuantum ? 'quantum' : isClassical ? 'classical' : 'hybrid'}
                    className="mx-auto"
                  />
                  <p className="mt-2 text-sm text-ink-muted">Confidence Score</p>
                </div>

                <div className="flex flex-col justify-center">
                  <div className="flex items-center gap-2 text-ink-muted">
                    <Clock className="h-4 w-4" />
                    <span className="text-sm">Expected Time</span>
                  </div>
                  <p className="mt-1 font-mono text-2xl font-semibold text-ink">{formatDurationMs(estimated_execution_time_ms)}</p>
                  <p className="text-xs text-ink-muted">Estimated execution</p>
                </div>

                <div className="flex flex-col justify-center">
                  <div className="flex items-center gap-2 text-ink-muted">
                    <DollarSign className="h-4 w-4" />
                    <span className="text-sm">Estimated Cost</span>
                  </div>
                  <p className="mt-1 font-mono text-2xl font-semibold text-ink">{formatCost(estimated_cost_usd)}</p>
                  <p className="text-xs text-ink-muted">Per execution</p>
                </div>

                <div className="flex flex-col justify-center">
                  <div className="flex items-center gap-2 text-ink-muted">
                    <Gauge className="h-4 w-4" />
                    <span className="text-sm">Quantum Probability</span>
                  </div>
                  <p className={`mt-1 font-mono text-2xl font-semibold ${isQuantum ? 'text-quantum' : 'text-ink'}`}>
                    {Math.round(recommendation.quantum_probability * 100)}%
                  </p>
                  <p className="text-xs text-ink-muted">Classical: {Math.round(recommendation.classical_probability * 100)}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </FadeIn>

        <div className="grid grid-cols-1 gap-4 md:gap-6 lg:grid-cols-2">
          <Card variant="glass">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-primary" />
                Model Analysis
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border border-hairline bg-surface-1 p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-ink">Recommended Hardware</span>
                  <Badge variant={getBadgeVariant()}>{recommendation.recommended_hardware}</Badge>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-ink-muted">Quantum Probability</span>
                    <span className="font-mono text-ink">{(recommendation.quantum_probability * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-ink-muted">Classical Probability</span>
                    <span className="font-mono text-ink">{(recommendation.classical_probability * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-ink-muted">Confidence</span>
                    <span className="font-mono font-semibold text-ink">{(recommendation.confidence * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {alternatives && alternatives.length > 0 && (
            <Card variant="glass">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <GitBranch className="h-5 w-5 text-ink" />
                  Alternative Options
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {alternatives.map((alt, idx) => (
                  <div key={idx} className="border border-hairline bg-surface-1 p-4">
                    <div className="flex items-center justify-between mb-2">
                      <Badge variant={alt.hardware === 'Quantum' ? 'quantum' : alt.hardware === 'Classical' ? 'classical' : 'hybrid'}>
                        {alt.hardware}
                      </Badge>
                      <span className="font-mono text-sm text-ink">{(alt.confidence * 100).toFixed(0)}% confidence</span>
                    </div>
                    <p className="text-xs text-ink-muted">{alt.trade_off}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>

        <Card variant="glass">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-primary" />
              Decision Rationale
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="border border-hairline bg-surface-1 p-4">
              <p className="text-sm leading-relaxed text-ink">{recommendation.rationale}</p>

              {estimated_cost_usd && estimated_execution_time_ms && (
                <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="flex items-center gap-2 text-sm text-ink">
                    <Clock className="h-4 w-4 text-ink-muted" />
                    <span>
                      Estimated time: <strong>{formatDurationMs(estimated_execution_time_ms)}</strong>
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-ink">
                    <DollarSign className="h-4 w-4 text-ink-muted" />
                    <span>
                      Estimated cost: <strong>{formatCost(estimated_cost_usd)}</strong>
                    </span>
                  </div>
                </div>
              )}
            </div>

            <div className="mt-4 flex gap-3 flex-wrap">
              <Button variant="outline" onClick={() => navigate('/decision-engine')}>
                Try Different Parameters
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  )
}
