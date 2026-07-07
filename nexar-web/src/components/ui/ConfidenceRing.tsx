import { cn } from '@/lib/utils'

export interface ConfidenceRingProps {
  value: number
  size?: number
  variant?: 'quantum' | 'classical' | 'hybrid'
  className?: string
}

const STROKE_BY_VARIANT: Record<NonNullable<ConfidenceRingProps['variant']>, string> = {
  quantum: 'stroke-quantum',
  classical: 'stroke-classical',
  hybrid: 'stroke-hybrid',
}

/** Shared SVG confidence ring -- extracted from the duplicated pattern in frontend's DecisionResults/PipelineDecisionResults. */
function ConfidenceRing({ value, size = 96, variant = 'quantum', className }: ConfidenceRingProps) {
  const radius = size / 2 - 6
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (Math.min(100, Math.max(0, value)) / 100) * circumference

  return (
    <div className={cn('relative inline-flex items-center justify-center', className)} style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={radius} strokeWidth={4} className="stroke-hairline" fill="none" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={4}
          fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="square"
          className={cn('transition-all duration-500', STROKE_BY_VARIANT[variant])}
        />
      </svg>
      <span className="absolute text-xl font-normal text-ink">{Math.round(value)}%</span>
    </div>
  )
}

export { ConfidenceRing }
