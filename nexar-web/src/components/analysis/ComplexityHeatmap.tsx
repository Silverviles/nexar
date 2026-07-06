/**
 * Complexity Heatmap Component
 * Visual representation of complexity across code sections
 */

import { Activity } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { ClassicalMetrics, QuantumMetrics } from '@/types/codeAnalysis'
import { cn } from '@/lib/utils'

interface ComplexityHeatmapProps {
  classicalMetrics?: ClassicalMetrics | null
  quantumMetrics?: QuantumMetrics | null
  isQuantum: boolean
}

export function ComplexityHeatmap({ classicalMetrics, quantumMetrics, isQuantum }: ComplexityHeatmapProps) {
  if (isQuantum && !quantumMetrics) return null
  if (!isQuantum && !classicalMetrics) return null

  return (
    <Card variant="glass">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-ink">
          <Activity className="h-5 w-5 text-primary" />
          Complexity Distribution
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {isQuantum && quantumMetrics ? (
          <QuantumComplexityView metrics={quantumMetrics} />
        ) : classicalMetrics ? (
          <ClassicalComplexityView metrics={classicalMetrics} />
        ) : null}
      </CardContent>
    </Card>
  )
}

/** Single severity-based color per bar (error/warning/success) -- replaces frontend's per-metric rainbow (purple/blue/cyan/orange/pink). */
function severityColorFor(percentage: number) {
  if (percentage > 75) return { bar: 'bg-error', badge: 'border-error/50 text-error', label: 'High' }
  if (percentage > 50) return { bar: 'bg-warning', badge: 'border-warning/60 text-ink', label: 'Medium' }
  return { bar: 'bg-success', badge: 'border-success/50 text-success', label: 'Low' }
}

function ClassicalComplexityView({ metrics }: { metrics: ClassicalMetrics }) {
  const complexityItems = [
    { label: 'Cyclomatic Complexity', value: metrics.cyclomatic_complexity, max: 20, description: 'Structural complexity (lower is better)' },
    { label: 'Cognitive Complexity', value: metrics.cognitive_complexity, max: 20, description: 'Mental complexity (lower is better)' },
    { label: 'Max Nesting Depth', value: metrics.max_nesting_depth, max: 10, description: 'Indentation levels (lower is better)' },
    { label: 'Loop Count', value: metrics.loop_count, max: 10, description: 'Number of loops (may indicate patterns)' },
    { label: 'Conditional Count', value: metrics.conditional_count, max: 15, description: 'IF/ELSE branches (higher = more paths)' },
  ]

  return (
    <div className="space-y-3">
      {complexityItems.map((item) => {
        const percentage = (item.value / item.max) * 100
        const severity = severityColorFor(percentage)

        return (
          <div key={item.label}>
            <div className="flex items-center justify-between mb-1">
              <div>
                <p className="text-sm font-semibold text-ink">{item.label}</p>
                <p className="text-xs text-ink-muted">{item.description}</p>
              </div>
              <div className="text-right">
                <span className="text-sm font-mono font-semibold text-ink">{item.value}</span>
                <Badge variant="outline" className={cn('ml-2', severity.badge)}>
                  {severity.label}
                </Badge>
              </div>
            </div>
            <div className="w-full bg-surface-2 h-2 overflow-hidden">
              <div className={cn('h-full transition-all', severity.bar)} style={{ width: `${Math.min(percentage, 100)}%` }} />
            </div>
          </div>
        )
      })}

      <div className="mt-4 pt-3 border-t border-hairline">
        <div className="flex items-center justify-between mb-2">
          <p className="text-sm font-semibold text-ink">Time Complexity</p>
          <Badge variant="outline" className="border-primary/40 text-primary">
            {metrics.time_complexity}
          </Badge>
        </div>
        <p className="text-xs text-ink-muted">{getTimeComplexityDescription(metrics.time_complexity)}</p>
      </div>

      <div>
        <div className="flex items-center justify-between mb-2">
          <p className="text-sm font-semibold text-ink">Space Complexity</p>
          <Badge variant="outline" className="border-primary/40 text-primary">
            {metrics.space_complexity}
          </Badge>
        </div>
        <p className="text-xs text-ink-muted">{getSpaceComplexityDescription(metrics.space_complexity)}</p>
      </div>
    </div>
  )
}

function QuantumComplexityView({ metrics }: { metrics: QuantumMetrics }) {
  const complexityItems = [
    { label: 'Qubit Count', value: metrics.qubits_required, max: 20, description: 'Number of qubits needed' },
    { label: 'Circuit Depth', value: metrics.circuit_depth, max: 50, description: 'Sequential gate layers' },
    { label: 'Gate Count', value: metrics.gate_count, max: 60, description: 'Total quantum gates' },
    {
      label: 'Entangling Gates Ratio',
      value: Math.round(metrics.cx_gate_ratio * 100),
      max: 100,
      description: '% of two-qubit gates',
      isPercentage: true,
    },
  ]

  return (
    <div className="space-y-3">
      {complexityItems.map((item) => {
        const percentage = item.isPercentage ? item.value : (item.value / item.max) * 100
        const severity = severityColorFor(percentage)

        return (
          <div key={item.label}>
            <div className="flex items-center justify-between mb-1">
              <div>
                <p className="text-sm font-semibold text-ink">{item.label}</p>
                <p className="text-xs text-ink-muted">{item.description}</p>
              </div>
              <div className="text-right">
                <span className="text-sm font-mono font-semibold text-ink">
                  {item.value}
                  {item.isPercentage ? '%' : ''}
                </span>
                <Badge variant="outline" className={cn('ml-2', severity.badge)}>
                  {severity.label}
                </Badge>
              </div>
            </div>
            <div className="w-full bg-surface-2 h-2 overflow-hidden">
              <div className={cn('h-full transition-all', severity.bar)} style={{ width: `${Math.min(percentage, 100)}%` }} />
            </div>
          </div>
        )
      })}

      <div className="mt-4 pt-3 border-t border-hairline space-y-2">
        <div className="flex items-center justify-between">
          <p className="text-sm font-semibold text-ink">Superposition Capability</p>
          <div className="flex items-center gap-2">
            <div className="h-2 w-12 bg-surface-2 overflow-hidden">
              <div className="h-full bg-quantum" style={{ width: `${Math.round(metrics.superposition_score * 100)}%` }} />
            </div>
            <span className="text-xs font-mono text-ink">{Math.round(metrics.superposition_score * 100)}%</span>
          </div>
        </div>
        <div className="flex items-center justify-between">
          <p className="text-sm font-semibold text-ink">Entanglement Capability</p>
          <div className="flex items-center gap-2">
            <div className="h-2 w-12 bg-surface-2 overflow-hidden">
              <div className="h-full bg-quantum" style={{ width: `${Math.round(metrics.entanglement_score * 100)}%` }} />
            </div>
            <span className="text-xs font-mono text-ink">{Math.round(metrics.entanglement_score * 100)}%</span>
          </div>
        </div>
      </div>
    </div>
  )
}

function getTimeComplexityDescription(complexity: string): string {
  const descriptions: Record<string, string> = {
    'O(1)': 'Constant time - excellent performance',
    'O(log n)': 'Logarithmic - very efficient',
    'O(n)': 'Linear - good scalability',
    'O(n log n)': 'Linearithmic - reasonable for large inputs',
    'O(n^2)': 'Quadratic - may be slow for large inputs',
    'O(n^3)': 'Cubic - poor scalability',
    'O(2^n)': 'Exponential - only suitable for small inputs',
    'O(sqrt(n))': 'Quantum advantage - Grover-like algorithm',
  }
  return descriptions[complexity] || 'Unknown complexity class'
}

function getSpaceComplexityDescription(complexity: string): string {
  const descriptions: Record<string, string> = {
    'O(1)': 'Constant space - minimal memory',
    'O(n)': 'Linear space - scales linearly with input',
    'O(n^2)': 'Quadratic space - significant memory usage',
    'O(n^3)': 'Cubic space - very high memory requirements',
  }
  return descriptions[complexity] || 'Unknown space complexity class'
}
