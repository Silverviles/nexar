import * as React from 'react'
import { Check } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type' | 'onChange'> {
  checked?: boolean
  onCheckedChange?: (checked: boolean) => void
}

const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, checked, onCheckedChange, ...props }, ref) => (
    <label className={cn('relative inline-flex h-4 w-4 shrink-0 items-center justify-center', className)}>
      <input
        type="checkbox"
        ref={ref}
        checked={checked}
        onChange={(e) => onCheckedChange?.(e.target.checked)}
        className="peer sr-only"
        {...props}
      />
      <span
        className={cn(
          'flex h-4 w-4 items-center justify-center rounded-none border border-hairline-strong bg-canvas peer-checked:bg-primary peer-checked:border-primary peer-focus-visible:carbon-focus'
        )}
      >
        {checked && <Check className="h-3 w-3 text-on-primary" />}
      </span>
    </label>
  )
)
Checkbox.displayName = 'Checkbox'

export { Checkbox }
