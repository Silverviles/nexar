import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Section } from '@/components/ui/Section'
import { FadeIn } from '@/components/ui/FadeIn'
import { AnimatedNumber } from '@/components/ui/AnimatedNumber'
import { CodeBlock } from '@/components/ui/CodeBlock'
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui/Accordion'
import { MarketingLayout } from '@/components/layout/MarketingLayout'
import { PipelineSteps } from '@/components/marketing/PipelineSteps'
import { HardwareBand } from '@/components/marketing/HardwareBand'
import { HeroBackground } from '@/components/marketing/HeroBackground'
import { LogoCloud } from '@/components/marketing/LogoCloud'
import { Testimonials } from '@/components/marketing/Testimonials'
import { ArrowRight, Brain, RefreshCw, Server, Wand2 } from 'lucide-react'
import { STATS, PRICING_TIERS, FAQS } from '@/lib/marketing-content'
import { cn } from '@/lib/utils'

const FEATURES = [
  {
    icon: Brain,
    title: 'ML-Driven Routing',
    description:
      'A trained classifier scores every workload and recommends quantum or classical execution with a confidence score and rationale.',
  },
  {
    icon: Wand2,
    title: 'Automatic Quantum Detection',
    description:
      'The AI converter recognizes classical patterns — search, optimization, factorization — that map onto known quantum algorithms.',
  },
  {
    icon: Server,
    title: 'Multi-Provider Execution',
    description: 'One interface routes to IBM Qiskit, AWS Braket, or Azure Quantum — simulators and real hardware.',
  },
  {
    icon: RefreshCw,
    title: 'Feedback-Driven Accuracy',
    description: 'Real execution outcomes feed back into the model, so routing recommendations keep improving.',
  },
]

const PREDICT_EXAMPLE_REQUEST = `POST /api/v1/decision-engine/predict
Authorization: Bearer <token>

{
  "problemType": "search",
  "qubits": 8,
  "gateCount": 96,
  "entanglementScore": 0.54
}`

const PREDICT_EXAMPLE_RESPONSE = `{
  "recommendedHardware": "quantum",
  "confidence": 0.91,
  "rationale": "Grover-style search pattern detected with favorable qubit count.",
  "estimatedCostUsd": 0.18
}`

function Landing() {
  return (
    <MarketingLayout>
      {/* Hero */}
      <section className="relative overflow-hidden container mx-auto px-6 py-24 md:py-32 text-center">
        <HeroBackground />
        <FadeIn className="relative z-10">
          <h1 className="text-5xl md:text-[76px] font-light leading-[1.17] tracking-[-0.5px] text-ink mb-6 max-w-4xl mx-auto">
            The Future of Hybrid Computing <span className="text-primary">Today</span>
          </h1>
          <p className="text-lg text-ink-muted mb-10 max-w-2xl mx-auto leading-relaxed">
            Intelligent workload routing between quantum and classical systems. Predict performance, optimize costs,
            and maximize efficiency with ML-driven decisions.
          </p>
          <div className="flex justify-center">
            <Link to="/signup">
              <Button size="xl">
                Sign Up for Free
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
        </FadeIn>
      </section>

      <LogoCloud />

      {/* Feature grid */}
      <section className="container mx-auto px-6 py-20">
        <FadeIn inView className="text-center mb-16">
          <h2 className="text-3xl md:text-[42px] font-light text-ink mb-4">Engineered for Excellence</h2>
          <p className="text-ink-muted max-w-2xl mx-auto">
            Built with cutting-edge technology to deliver unparalleled performance
          </p>
        </FadeIn>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-px bg-hairline max-w-6xl mx-auto border border-hairline">
          {FEATURES.map((feature, i) => (
            <FadeIn key={feature.title} delay={i * 0.05} inView>
              <Card className="group h-full border-0 hover:bg-surface-1">
                <CardContent className="p-8">
                  <div className="w-12 h-12 bg-surface-1 flex items-center justify-center mb-6 transition-colors group-hover:bg-primary">
                    <feature.icon className="h-6 w-6 text-primary transition-colors group-hover:text-on-primary" />
                  </div>
                  <h3 className="text-lg font-normal mb-3 text-ink">{feature.title}</h3>
                  <p className="text-ink-muted text-sm">{feature.description}</p>
                </CardContent>
              </Card>
            </FadeIn>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <PipelineSteps />

      {/* Code showcase */}
      <Section tone="surface">
        <div className="grid lg:grid-cols-2 gap-12 items-center max-w-6xl mx-auto">
          <FadeIn inView>
            <h2 className="text-3xl md:text-[42px] font-light text-ink mb-4">One call, one recommendation</h2>
            <p className="text-ink-muted mb-6 leading-relaxed">
              Send a workload's problem type and circuit metrics to the decision engine and get back a routing call —
              quantum or classical — with a confidence score and cost estimate, ready to act on.
            </p>
            <Link to="/docs" className="text-primary inline-flex items-center gap-1 hover:underline">
              Read the API docs
              <ArrowRight className="h-4 w-4" />
            </Link>
          </FadeIn>
          <FadeIn inView delay={0.1}>
            <CodeBlock code={PREDICT_EXAMPLE_REQUEST} className="mb-4" />
            <CodeBlock code={PREDICT_EXAMPLE_RESPONSE} />
          </FadeIn>
        </div>
      </Section>

      {/* Supported Hardware */}
      <HardwareBand />

      <Testimonials />

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

      {/* Pricing teaser */}
      <section className="container mx-auto px-6 py-20">
        <FadeIn inView className="text-center mb-16">
          <h2 className="text-3xl md:text-[42px] font-light text-ink mb-4">Simple, Transparent Pricing</h2>
          <p className="text-ink-muted max-w-2xl mx-auto">Start free, scale as your workloads grow</p>
        </FadeIn>

        <div className="grid md:grid-cols-3 gap-px bg-hairline max-w-6xl mx-auto border border-hairline">
          {PRICING_TIERS.map((tier, i) => (
            <FadeIn key={tier.name} delay={i * 0.05} inView>
              <Card
                variant={tier.highlight ? 'quantum' : 'default'}
                className={cn('h-full border-0 relative', !tier.highlight && 'hover:bg-surface-1')}
              >
                <CardContent className="p-8">
                  {tier.highlight && <Badge variant="quantum" className="absolute right-6 top-6">Most popular</Badge>}
                  <h3 className="text-xl font-normal mb-1 text-ink">{tier.name}</h3>
                  <div className="mb-4">
                    <span className="text-3xl font-light text-ink">{tier.price}</span>
                    <span className="text-ink-muted">{tier.period}</span>
                  </div>
                  <ul className="space-y-2 text-sm text-ink-muted">
                    {tier.features.slice(0, 3).map((feature) => (
                      <li key={feature}>{feature}</li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </FadeIn>
          ))}
        </div>

        <div className="text-center mt-10">
          <Link to="/pricing" className="text-primary inline-flex items-center gap-1 hover:underline">
            See full pricing
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>

      {/* FAQ */}
      <Section tone="surface">
        <FadeIn inView className="text-center mb-16">
          <h2 className="text-3xl md:text-[42px] font-light text-ink mb-4">Frequently Asked Questions</h2>
        </FadeIn>

        <FadeIn inView className="max-w-3xl mx-auto">
          <Accordion defaultValue={FAQS[0].question}>
            {FAQS.map((faq) => (
              <AccordionItem key={faq.question} value={faq.question}>
                <AccordionTrigger>{faq.question}</AccordionTrigger>
                <AccordionContent>{faq.answer}</AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </FadeIn>
      </Section>

      {/* CTA banner */}
      <section className="container mx-auto px-6 py-20">
        <FadeIn inView className="bg-primary text-on-primary p-12 text-center max-w-4xl mx-auto">
          <h2 className="text-3xl md:text-[32px] font-normal mb-4">Start your AI journey today</h2>
          <p className="text-on-primary/80 mb-8 max-w-2xl mx-auto">
            Join forward-thinking companies that are transforming their operations with AI.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/signup">
              <Button size="lg" variant="secondary" className="bg-canvas text-primary hover:bg-surface-1">
                Get Started Free
              </Button>
            </Link>
          </div>
          <p className="text-sm text-on-primary/70 mt-6">No credit card required · 14-day free trial</p>
        </FadeIn>
      </section>
    </MarketingLayout>
  )
}

export default Landing
