import * as React from 'react'
import { ChevronDown, Check } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useDismiss } from '@/hooks/use-dismiss'

interface SelectContextValue {
  value?: string
  onValueChange: (value: string) => void
  open: boolean
  setOpen: (open: boolean) => void
  label: React.ReactNode
  setLabel: (label: React.ReactNode) => void
}
const SelectContext = React.createContext<SelectContextValue | null>(null)
function useSelectContext() {
  const ctx = React.useContext(SelectContext)
  if (!ctx) throw new Error('Select subcomponents must be used within <Select>')
  return ctx
}

export interface SelectProps {
  value?: string
  defaultValue?: string
  onValueChange?: (value: string) => void
  children: React.ReactNode
}

function Select({ value: valueProp, defaultValue, onValueChange, children }: SelectProps) {
  const [open, setOpen] = React.useState(false)
  const [label, setLabel] = React.useState<React.ReactNode>(null)
  const [internal, setInternal] = React.useState(defaultValue)
  const value = valueProp ?? internal
  const handleValueChange = (v: string) => {
    setInternal(v)
    onValueChange?.(v)
  }
  return (
    <SelectContext.Provider value={{ value, onValueChange: handleValueChange, open, setOpen, label, setLabel }}>
      <div className="relative">{children}</div>
    </SelectContext.Provider>
  )
}

const SelectTrigger = React.forwardRef<HTMLButtonElement, React.ButtonHTMLAttributes<HTMLButtonElement>>(
  ({ className, children, ...props }, ref) => {
    const { open, setOpen } = useSelectContext()
    return (
      <button
        type="button"
        ref={ref}
        onClick={() => setOpen(!open)}
        className={cn(
          'flex h-10 w-full items-center justify-between rounded-none border-0 border-b border-hairline bg-surface-1 px-4 py-2 text-sm text-ink carbon-focus-input focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50',
          className
        )}
        {...props}
      >
        {children}
        <ChevronDown className="h-4 w-4 shrink-0 text-ink-muted" />
      </button>
    )
  }
)
SelectTrigger.displayName = 'SelectTrigger'

function SelectValue({ placeholder }: { placeholder?: string }) {
  const { label } = useSelectContext()
  return <span className={cn(!label && 'text-ink-subtle')}>{label ?? placeholder}</span>
}

function SelectContent({ children, className }: { children: React.ReactNode; className?: string }) {
  const { open, setOpen } = useSelectContext()
  const contentRef = React.useRef<HTMLDivElement>(null)
  useDismiss(contentRef, open, () => setOpen(false))
  if (!open) return null
  return (
    <div
      ref={contentRef}
      className={cn(
        'absolute z-50 mt-1 max-h-60 w-full overflow-auto border border-hairline bg-canvas py-1 shadow-none',
        className
      )}
    >
      {children}
    </div>
  )
}

function SelectItem({ value, children, className }: { value: string; children: React.ReactNode; className?: string }) {
  const ctx = useSelectContext()
  const selected = ctx.value === value
  React.useEffect(() => {
    if (selected) ctx.setLabel(children)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected])
  return (
    <div
      role="option"
      aria-selected={selected}
      onClick={() => {
        ctx.onValueChange(value)
        ctx.setLabel(children)
        ctx.setOpen(false)
      }}
      className={cn(
        'flex cursor-pointer items-center justify-between px-4 py-2 text-sm text-ink hover:bg-surface-1',
        selected && 'bg-surface-1',
        className
      )}
    >
      {children}
      {selected && <Check className="h-4 w-4 text-primary" />}
    </div>
  )
}

export { Select, SelectTrigger, SelectValue, SelectContent, SelectItem }
