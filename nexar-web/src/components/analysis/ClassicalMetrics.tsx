/**
 * Classical Metrics Display Component
 */

import { Code, GitBranch, Layers, Repeat, Zap, FileCode, CircleHelp } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { MetricCard } from './MetricCard'
import type { ClassicalMetrics } from '@/types/codeAnalysis'

interface ClassicalMetricsProps {
  metrics: ClassicalMetrics
  problemSize: number
}

export function ClassicalMetricsDisplay({ metrics, problemSize }: ClassicalMetricsProps) {
  const getComplexityColor = (complexity: number): 'default' | 'success' | 'warning' => {
    if (complexity <= 5) return 'success'
    if (complexity <= 10) return 'default'
    return 'warning'
  }

  return (
    <div className="space-y-4">
      <Card variant="glass" className="border-classical/30 bg-classical/5">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-classical">
            <Code className="h-5 w-5" />
            Classical Code Analysis
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <button
                    type="button"
                    className="inline-flex h-5 w-5 items-center justify-center text-ink-subtle hover:text-ink"
                    aria-label="Explain nesting depth metrics"
                  >
                    <CircleHelp className="h-4 w-4" />
                  </button>
                </TooltipTrigger>
                <TooltipContent className="max-w-xs">
                  <p>
                    <strong>Control-flow nesting</strong> counts only branching and loop depth (`if`/`for`/`while`).
                  </p>
                  <p className="mt-1">
                    <strong>Structural nesting</strong> also includes wrapper scopes like `class` and `def` blocks.
                  </p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline" className="border-classical/40 text-classical">
              Problem Size: {problemSize}
            </Badge>
            <Badge variant="outline" className="border-classical/40 text-classical">
              {metrics.time_complexity}
            </Badge>
            <Badge variant="outline" className="border-classical/40 text-classical">
              Space: {metrics.space_complexity}
            </Badge>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-4">
        <MetricCard
          icon={GitBranch}
          label="Cyclomatic Complexity"
          value={metrics.cyclomatic_complexity}
          subtitle={`Max fn: ${metrics.cyclomatic_complexity_max} | Cognitive: ${metrics.cognitive_complexity}`}
          variant={getComplexityColor(metrics.cyclomatic_complexity)}
          animate
        />
        <MetricCard icon={FileCode} label="Lines of Code" value={metrics.lines_of_code} subtitle="Analyzed lines" variant="classical" animate />
        <MetricCard icon={Repeat} label="Loop Count" value={metrics.loop_count} subtitle="Iterations detected" variant="classical" animate />
        <MetricCard icon={GitBranch} label="Conditionals" value={metrics.conditional_count} subtitle="Decision points" variant="classical" animate />
        <MetricCard
          icon={Layers}
          label="Control-Flow Nesting"
          value={metrics.max_nesting_depth}
          subtitle={`Structural: ${metrics.structural_nesting_depth}`}
          variant={metrics.max_nesting_depth > 3 ? 'warning' : 'success'}
          animate
        />
        <MetricCard
          icon={Layers}
          label="Structural Nesting"
          value={metrics.structural_nesting_depth}
          subtitle={`Control-flow: ${metrics.control_flow_nesting_depth}`}
          variant={metrics.structural_nesting_depth > 4 ? 'warning' : 'success'}
          animate
        />
        <MetricCard icon={Zap} label="Functions" value={metrics.function_count} subtitle="Defined functions" variant="classical" animate />
      </div>

      <Card variant="glass">
        <CardContent className="pt-6">
          <div className="space-y-2 text-sm">
            <p className="text-ink-muted">
              <span className="font-semibold text-ink">Time Complexity:</span> {metrics.time_complexity} indicates the algorithm's growth
              rate relative to input size.
            </p>
            <p className="text-ink-muted">
              <span className="font-semibold text-ink">Cyclomatic Complexity:</span>{' '}
              {metrics.cyclomatic_complexity <= 5 && 'Low complexity - easy to maintain and test.'}
              {metrics.cyclomatic_complexity > 5 && metrics.cyclomatic_complexity <= 10 && 'Moderate complexity - acceptable maintainability.'}
              {metrics.cyclomatic_complexity > 10 && 'High complexity - consider refactoring for better maintainability.'}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
