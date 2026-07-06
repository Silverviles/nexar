import * as React from 'react'
import { cn } from '@/lib/utils'

interface RadioGroupContextValue {
  value?: string
  onValueChange?: (value: string) => void
  name: string
}
const RadioGroupContext = React.createContext<RadioGroupContextValue | null>(null)

export interface RadioGroupProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'onChange'> {
  value?: string
  onValueChange?: (value: string) => void
  name?: string
}

const RadioGroup = React.forwardRef<HTMLDivElement, RadioGroupProps>(
  ({ className, value, onValueChange, name = 'radio-group', ...props }, ref) => (
    <RadioGroupContext.Provider value={{ value, onValueChange, name }}>
      <div ref={ref} role="radiogroup" className={cn('grid gap-2', className)} {...props} />
    </RadioGroupContext.Provider>
  )
)
RadioGroup.displayName = 'RadioGroup'

export interface RadioGroupItemProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  value: string
}

const RadioGroupItem = React.forwardRef<HTMLInputElement, RadioGroupItemProps>(
  ({ className, value, ...props }, ref) => {
    const ctx = React.useContext(RadioGroupContext)
    const checked = ctx?.value === value
    return (
      <label className={cn('relative inline-flex h-4 w-4 shrink-0 items-center justify-center', className)}>
        <input
          type="radio"
          ref={ref}
          name={ctx?.name}
          checked={checked}
          onChange={() => ctx?.onValueChange?.(value)}
          className="peer sr-only"
          {...props}
        />
        <span className="flex h-4 w-4 items-center justify-center rounded-full border border-hairline-strong bg-canvas peer-focus-visible:carbon-focus">
          {checked && <span className="h-2 w-2 rounded-full bg-primary" />}
        </span>
      </label>
    )
  }
)
RadioGroupItem.displayName = 'RadioGroupItem'

export { RadioGroup, RadioGroupItem }
