import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { FadeIn } from '@/components/ui/FadeIn'
import { Section } from '@/components/ui/Section'
import { AnimatedNumber } from '@/components/ui/AnimatedNumber'
import { MarketingLayout } from '@/components/layout/MarketingLayout'
import { PipelineSteps } from '@/components/marketing/PipelineSteps'
import { HardwareBand } from '@/components/marketing/HardwareBand'
import { DollarSign, GraduationCap, RefreshCw, Shuffle, Sparkles } from 'lucide-react'
import { STATS } from '@/lib/marketing-content'

const PRINCIPLES = [
  {
    icon: DollarSign,
    title: 'Cost-aware by default',
    description: 'Every recommendation ships with an estimated execution cost, not just a quantum-or-classical verdict.',
  },
  {
    icon: GraduationCap,
    title: 'No quantum expertise required',
    description: 'Submit code or problem parameters — the platform handles circuit-level and provider-level complexity.',
  },
  {
    icon: Shuffle,
    title: 'Provider-agnostic',
    description: 'One execution interface across IBM Qiskit, AWS Braket, and Azure Quantum. No hardware lock-in.',
  },
  {
    icon: RefreshCw,
    title: 'Improves with every run',
    description: 'Real execution outcomes are submitted back as feedback, sharpening future routing decisions.',
  },
]

function About() {
  return (
    <MarketingLayout>
      {/* Hero */}
      <section className="container mx-auto px-6 py-24 md:py-32 text-center">
        <FadeIn>
          <div className="inline-flex items-center gap-2 border border-primary/30 bg-surface-1 px-4 py-2 text-sm font-medium text-primary mb-8">
            <Sparkles className="h-4 w-4" />
            About Nexar
          </div>
          <h1 className="text-5xl md:text-[76px] font-light leading-[1.17] tracking-[-0.5px] text-ink mb-6 max-w-4xl mx-auto">
            Built to route work to the right kind of compute
          </h1>
          <p className="text-lg text-ink-muted mb-10 max-w-2xl mx-auto leading-relaxed">
            Not every problem belongs on quantum hardware, and not every problem belongs on classical hardware
            either. Nexar analyzes your code, detects where quantum algorithms actually help, and lets an ML model
            make the routing call — backed by a confidence score and a cost estimate, not a guess.
          </p>
        </FadeIn>
      </section>

      {/* Principles */}
      <section className="container mx-auto px-6 py-20">
        <FadeIn inView className="text-center mb-16">
          <h2 className="text-3xl md:text-[42px] font-light text-ink mb-4">What We Believe</h2>
          <p className="text-ink-muted max-w-2xl mx-auto">The principles behind every routing decision</p>
        </FadeIn>

        <div className="grid sm:grid-cols-2 gap-px bg-hairline max-w-4xl mx-auto border border-hairline">
          {PRINCIPLES.map((principle, i) => (
            <FadeIn key={principle.title} delay={i * 0.05} inView>
              <Card className="h-full border-0">
                <CardContent className="p-8">
                  <div className="w-12 h-12 bg-surface-1 flex items-center justify-center mb-6">
                    <principle.icon className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="text-lg font-normal mb-3 text-ink">{principle.title}</h3>
                  <p className="text-ink-muted text-sm">{principle.description}</p>
                </CardContent>
              </Card>
            </FadeIn>
          ))}
        </div>
      </section>

      {/* Pipeline */}
      <PipelineSteps />

      {/* Hardware */}
      <HardwareBand />

      {/* Stats */}
      <Section tone="surface">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {STATS.map((stat, i) => (
            <FadeIn key={stat.label} delay={i * 0.05} inView className="text-center">
              <div className="text-4xl font-light text-ink mb-2">
                <AnimatedNumber value={stat.value} />
              </div>
              <div className="text-ink-muted">{stat.label}</div>
            </FadeIn>
          ))}
        </div>
      </Section>

      {/* CTA banner */}
      <section className="container mx-auto px-6 py-20">
        <FadeIn inView className="bg-primary text-on-primary p-12 text-center max-w-4xl mx-auto">
          <h2 className="text-3xl md:text-[32px] font-normal mb-4">See Nexar in action</h2>
          <p className="text-on-primary/80 mb-8 max-w-2xl mx-auto">
            Submit your first workload and get a routing recommendation in seconds.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/signup">
              <Button size="lg" variant="secondary" className="bg-canvas text-primary hover:bg-surface-1">
                Get Started Free
              </Button>
            </Link>
          </div>
        </FadeIn>
      </section>
    </MarketingLayout>
  )
}

export default About
