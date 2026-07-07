import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

/*
  quantum/classical/hybrid are the compute-backend domain colors: IBM Blue,
  neutral gray, and semantic-success green -- see index.css theme comment.
  Each renders as a 1px border + tinted background + full-opacity text, which
  is Carbon's real outlined-tag pattern (not documented in DESIGN-ibm.md's
  marketing extraction, but consistent with its flat/hairline rules).
*/
const badgeVariants = cva(
  'inline-flex items-center rounded-none border px-2.5 py-0.5 text-xs font-medium tracking-[0.32px] transition-colors',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-primary text-on-primary',
        secondary: 'border-transparent bg-surface-2 text-ink',
        destructive: 'border-transparent bg-error text-on-primary',
        success: 'border-success/40 bg-success/10 text-success',
        warning: 'border-warning/60 bg-warning/15 text-ink',
        outline: 'border-hairline text-ink bg-transparent',
        quantum: 'border-quantum/40 bg-quantum/10 text-quantum',
        classical: 'border-classical/40 bg-classical/10 text-classical',
        hybrid: 'border-hybrid/40 bg-hybrid/10 text-hybrid',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant, className }))} {...props} />
}

export { Badge, badgeVariants }
