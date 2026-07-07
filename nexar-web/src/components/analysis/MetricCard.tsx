/**
 * Reusable Metric Card Component (analysis-scoped variant)
 */

import type { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'
import { FadeIn } from '@/components/ui/FadeIn'

interface MetricCardProps {
  icon: LucideIcon
  label: string
  value: string | number
  subtitle?: string
  variant?: 'default' | 'quantum' | 'classical' | 'success' | 'warning'
  className?: string
  animate?: boolean
}

const variantStyles = {
  default: 'border-hairline bg-surface-1',
  quantum: 'border-quantum/30 bg-quantum/5',
  classical: 'border-classical/30 bg-classical/5',
  success: 'border-success/30 bg-success/5',
  warning: 'border-warning/60 bg-warning/10',
}

const valueColorStyles = {
  default: 'text-ink',
  quantum: 'text-quantum',
  classical: 'text-classical',
  success: 'text-success',
  warning: 'text-ink',
}

function MetricCardInner({ icon: Icon, label, value, subtitle, variant = 'default', className }: MetricCardProps) {
  return (
    <div className={cn('border p-4 transition-colors', variantStyles[variant], className)}>
      <div className="flex items-center gap-2 text-sm text-ink-muted">
        <Icon className="h-4 w-4" />
        {label}
      </div>
      <p className={cn('mt-2 font-mono text-2xl font-semibold', valueColorStyles[variant])}>{value}</p>
      {subtitle && <p className="mt-1 text-xs text-ink-subtle">{subtitle}</p>}
    </div>
  )
}

export function MetricCard(props: MetricCardProps) {
  if (props.animate) {
    return (
      <FadeIn>
        <MetricCardInner {...props} />
      </FadeIn>
    )
  }
  return <MetricCardInner {...props} />
}
