import * as React from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { cn } from '@/lib/utils'

/* No-op provider kept for API parity with the shadcn TooltipProvider wrapper frontend mounts once in App.tsx. */
function TooltipProvider({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}

interface TooltipContextValue {
  open: boolean
  setOpen: (open: boolean) => void
}
const TooltipContext = React.createContext<TooltipContextValue | null>(null)

function Tooltip({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = React.useState(false)
  return (
    <TooltipContext.Provider value={{ open, setOpen }}>
      <span className="relative inline-flex" onMouseEnter={() => setOpen(true)} onMouseLeave={() => setOpen(false)}>
        {children}
      </span>
    </TooltipContext.Provider>
  )
}

function TooltipTrigger({ children }: { children: React.ReactNode; asChild?: boolean }) {
  return <>{children}</>
}

function TooltipContent({ children, className }: { children: React.ReactNode; className?: string }) {
  const ctx = React.useContext(TooltipContext)
  return (
    <AnimatePresence>
      {ctx?.open && (
        <motion.div
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 4 }}
          transition={{ duration: 0.15, ease: [0.4, 0, 0.2, 1] }}
          className={cn(
            'absolute bottom-full left-1/2 z-50 mb-2 -translate-x-1/2 whitespace-nowrap border border-hairline-strong bg-inverse-canvas px-3 py-1.5 text-xs text-inverse-ink',
            className
          )}
        >
          {children}
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export { TooltipProvider, Tooltip, TooltipTrigger, TooltipContent }
