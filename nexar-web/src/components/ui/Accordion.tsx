import * as React from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'

interface AccordionContextValue {
  openValue: string | null
  toggle: (value: string) => void
}
const AccordionContext = React.createContext<AccordionContextValue | null>(null)
function useAccordionContext() {
  const ctx = React.useContext(AccordionContext)
  if (!ctx) throw new Error('Accordion subcomponents must be used within <Accordion>')
  return ctx
}

const ItemContext = React.createContext<string | null>(null)
function useItemValue() {
  const value = React.useContext(ItemContext)
  if (value === null) throw new Error('AccordionTrigger/AccordionContent must be used within <AccordionItem>')
  return value
}

interface AccordionProps {
  defaultValue?: string
  className?: string
  children: React.ReactNode
}

function Accordion({ defaultValue, className, children }: AccordionProps) {
  const [openValue, setOpenValue] = React.useState<string | null>(defaultValue ?? null)
  const toggle = (value: string) => setOpenValue((v) => (v === value ? null : value))
  return (
    <AccordionContext.Provider value={{ openValue, toggle }}>
      <div className={cn('border-t border-hairline', className)}>{children}</div>
    </AccordionContext.Provider>
  )
}

function AccordionItem({ value, className, children }: { value: string; className?: string; children: React.ReactNode }) {
  return (
    <ItemContext.Provider value={value}>
      <div className={cn('border-b border-hairline', className)}>{children}</div>
    </ItemContext.Provider>
  )
}

function AccordionTrigger({ className, children }: { className?: string; children: React.ReactNode }) {
  const value = useItemValue()
  const { openValue, toggle } = useAccordionContext()
  const isOpen = openValue === value
  return (
    <button
      type="button"
      onClick={() => toggle(value)}
      aria-expanded={isOpen}
      className={cn(
        'flex w-full items-center justify-between gap-4 py-5 text-left text-base text-ink',
        className
      )}
    >
      {children}
      <motion.span
        animate={{ rotate: isOpen ? 180 : 0 }}
        transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
        className="shrink-0"
      >
        <ChevronDown className="h-5 w-5 text-ink-muted" />
      </motion.span>
    </button>
  )
}

function AccordionContent({ className, children }: { className?: string; children: React.ReactNode }) {
  const value = useItemValue()
  const { openValue } = useAccordionContext()
  const isOpen = openValue === value
  return (
    <AnimatePresence initial={false}>
      {isOpen && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
          className="overflow-hidden"
        >
          <div className={cn('pb-5 text-ink-muted', className)}>{children}</div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export { Accordion, AccordionItem, AccordionTrigger, AccordionContent }
