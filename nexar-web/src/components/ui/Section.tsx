import type { HTMLAttributes, ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface SectionProps extends HTMLAttributes<HTMLElement> {
  tone?: 'canvas' | 'surface'
  children: ReactNode
}

function Section({ tone = 'canvas', className, children, ...props }: SectionProps) {
  return (
    <section className={cn(tone === 'surface' && 'bg-surface-1', className)} {...props}>
      <div className="container mx-auto px-6 py-20">{children}</div>
    </section>
  )
}

export { Section }
