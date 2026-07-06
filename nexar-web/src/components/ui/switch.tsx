import * as React from 'react'
import { cn } from '@/lib/utils'

export interface SwitchProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type' | 'onChange'> {
  checked?: boolean
  onCheckedChange?: (checked: boolean) => void
}

const Switch = React.forwardRef<HTMLInputElement, SwitchProps>(
  ({ className, checked, onCheckedChange, ...props }, ref) => (
    <label className={cn('relative inline-flex h-5 w-9 shrink-0 items-center', className)}>
      <input
        type="checkbox"
        ref={ref}
        checked={checked}
        onChange={(e) => onCheckedChange?.(e.target.checked)}
        className="peer sr-only"
        {...props}
      />
      <span className="h-5 w-9 rounded-full bg-surface-2 transition-colors peer-checked:bg-primary peer-focus-visible:carbon-focus" />
      <span className="absolute left-0.5 h-4 w-4 rounded-full bg-canvas transition-transform peer-checked:translate-x-4" />
    </label>
  )
)
Switch.displayName = 'Switch'

export { Switch }
