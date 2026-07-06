import type { ReactNode, FC } from 'react'
import { Link } from 'react-router-dom'
import { Logo } from '@/components/layout/Logo'

interface AuthLayoutProps {
  children: ReactNode
  title: string
  description: string
}

const FEATURES = ['Real-time Analytics', 'Cost Optimization', 'ML Models', 'Hardware Abstraction']

const AuthLayout: FC<AuthLayoutProps> = ({ children, title, description }) => {
  return (
    <div className="min-h-screen flex">
      {/* Left: branding panel -- flat surface-1 + Carbon's documented soft blue-to-white gradient wash,
          replacing frontend's dark photo/glow blobs which contradict Carbon's flat aesthetic. */}
      <div className="hidden lg:flex lg:w-1/2 bg-surface-1 relative overflow-hidden border-r border-hairline">
        <div
          className="absolute inset-0"
          style={{ background: 'linear-gradient(135deg, rgba(15,98,254,0.08), rgba(255,255,255,0) 60%)' }}
        />

        <div className="relative z-10 flex flex-col justify-between p-12 text-ink">
          <Link to="/" className="flex flex-col items-start gap-3">
            <Logo linkTo={null} className="h-10" />
            <p className="text-sm text-ink-muted">Intelligent Quantum-Classical Workload Orchestration Platform</p>
          </Link>

          <div className="space-y-6">
            <div className="space-y-4">
              <div className="inline-block border border-primary/30 bg-canvas px-4 py-2 text-sm font-medium text-primary">
                AI-Powered Intelligence
              </div>
              <h2 className="text-5xl font-light leading-tight text-ink">
                Optimize Your Code
                <br />
                <span className="text-primary">Execution</span>
              </h2>
              <p className="text-lg text-ink-muted max-w-md">
                Make intelligent decisions with our advanced AI engine. Analyze, decide, and execute with confidence.
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              {FEATURES.map((feature) => (
                <div key={feature} className="border border-hairline bg-canvas px-4 py-2 text-xs text-ink-muted">
                  {feature}
                </div>
              ))}
            </div>
          </div>

          <div className="text-sm text-ink-subtle">
            <p>&copy; 2026 Nexar. All rights reserved.</p>
          </div>
        </div>
      </div>

      {/* Right: form panel */}
      <div className="flex-1 flex items-center justify-center p-8 bg-canvas">
        <div className="w-full max-w-md space-y-8">
          <div className="lg:hidden text-center">
            <Link to="/" className="inline-flex flex-col items-center gap-2">
              <Logo linkTo={null} className="h-8" />
              <p className="text-xs text-ink-muted">Intelligent Quantum-Classical Workload Orchestration Platform</p>
            </Link>
          </div>

          <div className="text-center lg:text-left space-y-2">
            <h1 className="text-3xl font-light tracking-tight text-ink">{title}</h1>
            <p className="text-ink-muted">{description}</p>
          </div>

          <div>{children}</div>

          <div className="lg:hidden text-center">
            <Link to="/" className="text-sm text-ink-muted hover:text-ink transition-colors">
              ← Back to home
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AuthLayout
