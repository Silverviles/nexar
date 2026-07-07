import { useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard,
  Code,
  Activity,
  History,
  Brain,
  Wallet,
  Settings,
  Server,
  ChevronLeft,
  ChevronRight,
  Menu,
  X,
  Sparkles,
  Workflow,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { Logo } from '@/components/layout/Logo'

const navGroups = [
  {
    heading: 'Overview',
    items: [{ icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' }],
  },
  {
    heading: 'Build & Analyze',
    items: [
      { icon: Workflow, label: 'Run Pipeline', path: '/pipeline' },
      { icon: Code, label: 'Code Analysis', path: '/analysis' },
      { icon: Sparkles, label: 'Python → Quantum', path: '/ai-converter' },
      { icon: Sparkles, label: 'AST Pattern Analyzer', path: '/ast-pattern-analyzer' },
    ],
  },
  {
    heading: 'Operate',
    items: [
      { icon: Activity, label: 'Decision Engine', path: '/decision-engine' },
      { icon: History, label: 'Execution History', path: '/history' },
      { icon: Server, label: 'Hardware Status', path: '/hardware' },
    ],
  },
  {
    heading: 'Manage',
    items: [
      { icon: Brain, label: 'ML Models', path: '/models' },
      { icon: Wallet, label: 'Cost Management', path: '/costs' },
      { icon: Settings, label: 'Settings', path: '/settings' },
    ],
  },
]

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()

  return (
    <>
      <Button
        variant="ghost"
        size="icon"
        className="fixed left-4 top-4 z-50 md:hidden bg-canvas border border-hairline"
        onClick={() => setMobileOpen(!mobileOpen)}
      >
        {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </Button>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-ink/50 md:hidden"
            onClick={() => setMobileOpen(false)}
          />
        )}
      </AnimatePresence>

      <motion.aside
        animate={{ width: collapsed ? 64 : 256 }}
        transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
        className={cn(
          'fixed left-0 top-0 z-40 h-screen border-r border-hairline bg-canvas md:translate-x-0 transition-transform duration-200',
          mobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        )}
      >
        <div className="flex h-full flex-col">
          <div className="flex h-16 items-center justify-between border-b border-hairline px-4">
            <div className="flex items-center gap-3">
              {collapsed ? (
                <Logo variant="mark" linkTo={null} className="h-8 w-8" />
              ) : (
                <div>
                  <Logo linkTo={null} className="h-6" />
                  <p className="mt-1 text-[10px] text-ink-subtle">Quantum Computing</p>
                </div>
              )}
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="hidden h-8 w-8 md:flex"
              onClick={() => setCollapsed(!collapsed)}
            >
              {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
            </Button>
          </div>

          <nav className="flex-1 space-y-4 overflow-y-auto p-3">
            {navGroups.map((group) => (
              <div key={group.heading}>
                {!collapsed && (
                  <p className="mb-1 px-3 text-[10px] font-semibold uppercase tracking-wider text-ink-subtle">
                    {group.heading}
                  </p>
                )}
                <div className="space-y-1">
                  {group.items.map((item) => {
                    const isActive = location.pathname === item.path
                    const Icon = item.icon

                    const linkContent = (
                      <NavLink
                        to={item.path}
                        onClick={() => setMobileOpen(false)}
                        className={cn(
                          'flex items-center gap-3 border-l-[3px] px-3 py-2.5 text-sm transition-colors',
                          isActive
                            ? 'border-l-primary bg-surface-1 text-ink font-semibold'
                            : 'border-l-transparent text-ink-muted hover:bg-surface-1 hover:text-ink'
                        )}
                      >
                        <Icon className={cn('h-5 w-5 shrink-0', isActive && 'text-primary')} />
                        {!collapsed && <span>{item.label}</span>}
                      </NavLink>
                    )

                    if (collapsed) {
                      return (
                        <Tooltip key={item.path}>
                          <TooltipTrigger asChild>{linkContent}</TooltipTrigger>
                          <TooltipContent>{item.label}</TooltipContent>
                        </Tooltip>
                      )
                    }

                    return <div key={item.path}>{linkContent}</div>
                  })}
                </div>
              </div>
            ))}
          </nav>

          <div className="border-t border-hairline p-3">
            {!collapsed && (
              <div className="bg-surface-1 p-3">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 animate-pulse rounded-full bg-success" />
                  <span className="text-xs text-ink-muted">System Online</span>
                </div>
                <p className="mt-1 font-mono text-[10px] text-ink-subtle">v2.1.0</p>
              </div>
            )}
          </div>
        </div>
      </motion.aside>
    </>
  )
}
