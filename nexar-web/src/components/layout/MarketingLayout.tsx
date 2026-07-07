import { useState, type ReactNode } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { Menu, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ThemeToggle } from '@/components/ui/ThemeToggle'
import { Logo } from '@/components/layout/Logo'
import { cn } from '@/lib/utils'

const NAV_LINKS = [
  { label: 'About', to: '/about' },
  { label: 'Use Cases', to: '/use-cases' },
  { label: 'Pricing', to: '/pricing' },
  { label: 'Docs', to: '/docs' },
]

const FOOTER_COLUMNS = [
  {
    heading: 'Product',
    links: [
      { label: 'About', to: '/about' },
      { label: 'Use Cases', to: '/use-cases' },
      { label: 'Pricing', to: '/pricing' },
      { label: 'Docs', to: '/docs' },
    ],
  },
  {
    heading: 'Company',
    links: [
      { label: 'About', to: '/about' },
      { label: 'Contact', to: '/contact' },
    ],
  },
]

function MarketingNav() {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <nav className="relative border-b border-hairline">
      <div className="container mx-auto flex h-16 items-center justify-between px-6">
        <Logo className="h-8" />

        <div className="hidden md:flex items-center gap-8">
          {NAV_LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                cn(
                  'relative py-1 text-sm transition-colors',
                  isActive ? 'text-ink font-medium' : 'text-ink-muted hover:text-ink'
                )
              }
            >
              {({ isActive }) => (
                <>
                  {link.label}
                  {isActive && (
                    <motion.span
                      layoutId="nav-underline"
                      className="absolute -bottom-1 left-0 right-0 h-0.5 bg-primary"
                      transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
                    />
                  )}
                </>
              )}
            </NavLink>
          ))}
        </div>

        <div className="hidden md:flex items-center gap-6">
          <ThemeToggle />
          <Link to="/signin">
            <Button variant="ghost">Sign In</Button>
          </Link>
          <Link to="/signup">
            <Button>Get Started</Button>
          </Link>
        </div>

        <button
          type="button"
          className="md:hidden text-ink"
          onClick={() => setMobileOpen((v) => !v)}
          aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
        >
          {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
            className="fixed inset-0 z-40 bg-ink/50 md:hidden"
            onClick={() => setMobileOpen(false)}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
            className="absolute inset-x-0 top-full z-50 border-b border-hairline bg-canvas md:hidden"
          >
            <div className="flex flex-col">
              {NAV_LINKS.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  onClick={() => setMobileOpen(false)}
                  className={({ isActive }) =>
                    cn(
                      'border-b border-hairline px-6 py-3 text-sm',
                      isActive ? 'text-ink font-medium' : 'text-ink-muted'
                    )
                  }
                >
                  {link.label}
                </NavLink>
              ))}
              <Link
                to="/contact"
                onClick={() => setMobileOpen(false)}
                className="border-b border-hairline px-6 py-3 text-sm text-ink-muted"
              >
                Contact
              </Link>

              <div className="flex flex-col gap-3 p-6">
                <Link to="/signin" onClick={() => setMobileOpen(false)}>
                  <Button variant="ghost" className="w-full">
                    Sign In
                  </Button>
                </Link>
                <Link to="/signup" onClick={() => setMobileOpen(false)}>
                  <Button className="w-full">Get Started</Button>
                </Link>
                <div className="flex items-center justify-between pt-2">
                  <span className="text-sm text-ink-muted">Theme</span>
                  <ThemeToggle />
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  )
}

function MarketingFooter() {
  return (
    <footer className="bg-inverse-canvas text-inverse-ink-muted py-16 px-6">
      <div className="container mx-auto">
        <div className="grid grid-cols-2 gap-8 pb-12 mb-12 border-b border-inverse-surface-1 md:grid-cols-4">
          <div className="col-span-2 md:col-span-1">
            <Logo inverse className="h-7" />
            <p className="mt-4 max-w-xs text-sm">
              Intelligent workload routing between quantum and classical systems.
            </p>
          </div>

          {FOOTER_COLUMNS.map((column) => (
            <div key={column.heading}>
              <div className="mb-4 text-sm font-medium text-inverse-ink">{column.heading}</div>
              <div className="flex flex-col gap-3">
                {column.links.map((link) => (
                  <Link key={link.label + link.to} to={link.to} className="text-sm hover:text-inverse-ink">
                    {link.label}
                  </Link>
                ))}
              </div>
            </div>
          ))}

          <div>
            <div className="mb-4 text-sm font-medium text-inverse-ink">Legal</div>
            <div className="flex flex-col gap-3">
              <span className="text-sm opacity-60">Privacy</span>
              <span className="text-sm opacity-60">Terms</span>
            </div>
          </div>
        </div>

        <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-sm">
          <div>&copy; {new Date().getFullYear()} Nexar. All rights reserved.</div>
          <Link to="/contact" className="hover:text-inverse-ink">
            Contact
          </Link>
        </div>
      </div>
    </footer>
  )
}

function MarketingLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-canvas text-ink">
      <div className="hidden md:flex h-8 items-center justify-end gap-6 bg-surface-1 px-6 text-xs text-ink-muted">
        <span>nexar.dev</span>
        <Link to="/contact" className="hover:text-ink">
          Contact
        </Link>
      </div>

      <MarketingNav />

      {children}

      <MarketingFooter />
    </div>
  )
}

export { MarketingLayout }
