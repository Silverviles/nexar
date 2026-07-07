import { Link } from 'react-router-dom'
import { ArrowRight, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { FadeIn } from '@/components/ui/FadeIn'
import { CodeBlock } from '@/components/ui/CodeBlock'
import { Section } from '@/components/ui/Section'
import { MarketingLayout } from '@/components/layout/MarketingLayout'
import { USE_CASES, PROBLEM_TYPES } from '@/lib/marketing-content'

const BEFORE_CODE = `def linear_search(items, target):
    for i, value in enumerate(items):
        if value == target:
            return i
    return -1`

const AFTER_CODE = `# Detected pattern: linear_search -> Grover's Algorithm
qc = QuantumCircuit(n_qubits)
qc.h(range(n_qubits))          # superposition over all indices
qc.append(oracle(target), range(n_qubits))
qc.append(diffusion(n_qubits), range(n_qubits))
qc.measure_all()               # ~sqrt(N) queries instead of N`

function UseCases() {
  return (
    <MarketingLayout>
      {/* Hero */}
      <section className="container mx-auto px-6 py-24 md:py-32 text-center">
        <FadeIn>
          <div className="inline-flex items-center gap-2 border border-primary/30 bg-surface-1 px-4 py-2 text-sm font-medium text-primary mb-8">
            <Sparkles className="h-4 w-4" />
            Use Cases
          </div>
          <h1 className="text-5xl md:text-[76px] font-light leading-[1.17] tracking-[-0.5px] text-ink mb-6 max-w-4xl mx-auto">
            From classical bottleneck to quantum speedup
          </h1>
          <p className="text-lg text-ink-muted mb-10 max-w-2xl mx-auto leading-relaxed">
            Nexar's AI code converter recognizes classical patterns that map cleanly onto known quantum algorithms —
            and tells you the expected speedup before you commit hardware time.
          </p>
        </FadeIn>
      </section>

      {/* Pattern cards */}
      <section className="container mx-auto px-6 py-20">
        <div className="grid md:grid-cols-3 gap-px bg-hairline max-w-6xl mx-auto border border-hairline">
          {USE_CASES.map((useCase, i) => (
            <FadeIn key={useCase.pattern} delay={i * 0.05} inView>
              <Card className="h-full border-0">
                <CardContent className="p-8">
                  <div className="text-sm text-ink-muted mb-2">{useCase.pattern}</div>
                  <h3 className="text-xl font-normal mb-4 text-ink flex items-center gap-2">
                    <ArrowRight className="h-4 w-4 text-primary shrink-0" />
                    {useCase.algorithm}
                  </h3>
                  <Badge variant="quantum" className="mb-4">
                    {useCase.speedup}
                  </Badge>
                  <p className="text-ink-muted text-sm leading-relaxed">{useCase.why}</p>
                </CardContent>
              </Card>
            </FadeIn>
          ))}
        </div>
      </section>

      {/* Before/after code example */}
      <Section tone="surface">
        <FadeIn inView className="text-center mb-16">
          <h2 className="text-3xl md:text-[42px] font-light text-ink mb-4">See a Conversion</h2>
          <p className="text-ink-muted max-w-2xl mx-auto">Linear search, detected and translated automatically</p>
        </FadeIn>

        <div className="grid lg:grid-cols-2 gap-8 max-w-5xl mx-auto">
          <FadeIn inView>
            <p className="text-sm text-ink-subtle mb-3">Before — classical Python</p>
            <CodeBlock code={BEFORE_CODE} />
          </FadeIn>
          <FadeIn inView delay={0.1}>
            <p className="text-sm text-ink-subtle mb-3">After — translated to Qiskit</p>
            <CodeBlock code={AFTER_CODE} />
          </FadeIn>
        </div>
      </Section>

      {/* Problem types */}
      <section className="container mx-auto px-6 py-20">
        <FadeIn inView className="text-center mb-12">
          <h2 className="text-3xl md:text-[42px] font-light text-ink mb-4">Problem Types We Classify</h2>
          <p className="text-ink-muted max-w-2xl mx-auto">Every submission is classified before it's routed</p>
        </FadeIn>
        <FadeIn inView className="flex flex-wrap justify-center gap-3 max-w-3xl mx-auto">
          {PROBLEM_TYPES.map((type) => (
            <Badge key={type} variant="outline">
              {type}
            </Badge>
          ))}
        </FadeIn>
      </section>

      {/* CTA banner */}
      <section className="container mx-auto px-6 py-20">
        <FadeIn inView className="bg-primary text-on-primary p-12 text-center max-w-4xl mx-auto">
          <h2 className="text-3xl md:text-[32px] font-normal mb-4">Try it on your code</h2>
          <p className="text-on-primary/80 mb-8 max-w-2xl mx-auto">
            See which of your workloads are quantum-suitable in minutes.
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

export default UseCases
