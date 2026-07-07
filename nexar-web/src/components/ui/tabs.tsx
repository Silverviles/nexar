import * as React from 'react'
import { cn } from '@/lib/utils'

interface TabsContextValue {
  value: string
  setValue: (value: string) => void
}
const TabsContext = React.createContext<TabsContextValue | null>(null)
function useTabsContext() {
  const ctx = React.useContext(TabsContext)
  if (!ctx) throw new Error('Tabs subcomponents must be used within <Tabs>')
  return ctx
}

export interface TabsProps {
  value?: string
  defaultValue?: string
  onValueChange?: (value: string) => void
  className?: string
  children: React.ReactNode
}

function Tabs({ value, defaultValue, onValueChange, className, children }: TabsProps) {
  const [internal, setInternal] = React.useState(defaultValue ?? '')
  const active = value ?? internal
  const setValue = (v: string) => {
    setInternal(v)
    onValueChange?.(v)
  }
  return (
    <TabsContext.Provider value={{ value: active, setValue }}>
      <div className={className}>{children}</div>
    </TabsContext.Provider>
  )
}

const TabsList = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('inline-flex items-center border-b border-hairline', className)} {...props} />
  )
)
TabsList.displayName = 'TabsList'

const TabsTrigger = React.forwardRef<HTMLButtonElement, React.ButtonHTMLAttributes<HTMLButtonElement> & { value: string }>(
  ({ className, value, ...props }, ref) => {
    const ctx = useTabsContext()
    const active = ctx.value === value
    return (
      <button
        ref={ref}
        type="button"
        onClick={() => ctx.setValue(value)}
        className={cn(
          'px-5 py-3 text-sm tracking-[0.16px] border-b-2 -mb-px transition-colors',
          active ? 'border-primary text-ink font-semibold' : 'border-transparent text-ink-muted hover:text-ink',
          className
        )}
        {...props}
      />
    )
  }
)
TabsTrigger.displayName = 'TabsTrigger'

const TabsContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement> & { value: string }>(
  ({ className, value, ...props }, ref) => {
    const ctx = useTabsContext()
    if (ctx.value !== value) return null
    return <div ref={ref} className={cn('mt-4', className)} {...props} />
  }
)
TabsContent.displayName = 'TabsContent'

export { Tabs, TabsList, TabsTrigger, TabsContent }
