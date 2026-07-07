/**
 * Code Quality Score Component
 * Displays overall code quality metrics with detailed breakdown
 */

import { useState } from 'react'
import { AlertCircle, TrendingUp, Gauge } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import type { CodeQualityMetrics } from '@/types/codeAnalysis'
import { cn } from '@/lib/utils'

interface CodeQualityScoreProps {
  metrics: CodeQualityMetrics
}

export function CodeQualityScore({ metrics }: CodeQualityScoreProps) {
  const [open, setOpen] = useState(false)

  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'text-success'
    if (score >= 60) return 'text-primary'
    if (score >= 40) return 'text-ink'
    return 'text-error'
  }

  const getCertaintyLevel = (score: number): 'Excellent' | 'Good' | 'Fair' | 'Poor' => {
    if (score >= 80) return 'Excellent'
    if (score >= 60) return 'Good'
    if (score >= 40) return 'Fair'
    return 'Poor'
  }

  return (
    <Card variant="glass" className="border-primary/30 bg-primary/5">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-primary">
            <Gauge className="h-5 w-5" />
            Code Quality Assessment
          </div>
          <Badge variant="outline" className="border-primary/40 text-primary">
            {getCertaintyLevel(metrics.overall_score)}
          </Badge>
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="flex items-center justify-between border border-hairline bg-surface-1 p-4">
          <div>
            <p className="text-xs text-ink-muted">Overall Score</p>
            <p className={cn('text-3xl font-semibold', getScoreColor(metrics.overall_score))}>{metrics.overall_score.toFixed(1)}/100</p>
          </div>
          <div className="flex h-20 w-20 items-center justify-center border-2 border-primary bg-canvas">
            <div className="text-center">
              <div className="text-xl font-semibold text-primary">{metrics.overall_score.toFixed(0)}%</div>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <div>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-ink-muted">Maintainability</span>
              <span className="font-mono text-xs font-semibold text-ink">{metrics.maintainability_score.toFixed(0)}/100</span>
            </div>
            <Progress value={metrics.maintainability_score} className="h-2" />
          </div>

          <div>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-ink-muted">Performance</span>
              <span className="font-mono text-xs font-semibold text-ink">{metrics.performance_score.toFixed(0)}/100</span>
            </div>
            <Progress value={metrics.performance_score} className="h-2" />
          </div>

          <div>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-ink-muted">Resource Efficiency</span>
              <span className="font-mono text-xs font-semibold text-ink">{metrics.resource_efficiency_score.toFixed(0)}/100</span>
            </div>
            <Progress value={metrics.resource_efficiency_score} className="h-2" />
          </div>

          <div className="flex items-center gap-2 border border-warning/50 bg-warning/10 p-3">
            <AlertCircle className="h-4 w-4 text-ink" />
            <div>
              <p className="text-xs text-ink-muted">Complexity Rating</p>
              <p className="font-semibold text-ink">{metrics.code_complexity_rating}</p>
            </div>
          </div>
        </div>

        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" className="w-full gap-2" size="sm">
              <TrendingUp className="h-4 w-4" />
              View Detailed Analysis
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Quality Metrics Breakdown</DialogTitle>
              <DialogDescription>Detailed analysis of code quality indicators</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="border border-hairline p-4">
                <h4 className="font-semibold mb-2 text-ink">Maintainability ({metrics.maintainability_score.toFixed(1)}/100)</h4>
                <p className="text-xs text-ink-muted mb-2">
                  Measures how easy the code is to understand and modify. Affected by cyclomatic complexity and nesting depth.
                </p>
                <Progress value={metrics.maintainability_score} className="h-2" />
              </div>

              <div className="border border-hairline p-4">
                <h4 className="font-semibold mb-2 text-ink">Performance ({metrics.performance_score.toFixed(1)}/100)</h4>
                <p className="text-xs text-ink-muted mb-2">
                  Evaluates algorithm efficiency and resource utilization. Lower time complexity indicates better performance.
                </p>
                <Progress value={metrics.performance_score} className="h-2" />
              </div>

              <div className="border border-hairline p-4">
                <h4 className="font-semibold mb-2 text-ink">Resource Efficiency ({metrics.resource_efficiency_score.toFixed(1)}/100)</h4>
                <p className="text-xs text-ink-muted mb-2">
                  Assessment of memory and computational resource usage. Lower space complexity is better.
                </p>
                <Progress value={metrics.resource_efficiency_score} className="h-2" />
              </div>

              <div className="border border-warning/50 bg-warning/10 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <AlertCircle className="h-4 w-4 text-ink" />
                  <h4 className="font-semibold text-ink">Complexity Rating</h4>
                </div>
                <p className="text-sm text-ink">{metrics.code_complexity_rating}</p>
                <p className="text-xs text-ink-muted mt-2">
                  {metrics.code_complexity_rating === 'Very High'
                    ? 'Consider refactoring: High complexity increases bug risk and maintenance effort.'
                    : metrics.code_complexity_rating === 'High'
                      ? 'Monitor complexity: Consider structural improvements for better maintainability.'
                      : 'Good complexity level for this code type.'}
                </p>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  )
}
