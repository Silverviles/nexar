import { FadeIn } from '@/components/ui/FadeIn'
import { Section } from '@/components/ui/Section'
import { PIPELINE_STEPS } from '@/lib/marketing-content'

function PipelineSteps() {
  return (
    <Section>
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-[42px] font-light text-ink mb-4">How It Works</h2>
        <p className="text-ink-muted max-w-2xl mx-auto">
          One pipeline, four stages, from raw code to a hardware decision
        </p>
      </div>

      <div className="grid md:grid-cols-4 gap-8 max-w-6xl mx-auto border-t border-hairline pt-10">
        {PIPELINE_STEPS.map((step, i) => (
          <FadeIn key={step.step} delay={i * 0.08} inView>
            <div className="text-3xl font-light text-primary mb-3 font-mono">{step.step}</div>
            <h3 className="text-xl font-normal text-ink mb-2">{step.title}</h3>
            <p className="text-ink-muted text-sm mb-2">{step.description}</p>
            <p className="font-mono text-xs text-ink-subtle">{step.service}</p>
          </FadeIn>
        ))}
      </div>
    </Section>
  )
}

export { PipelineSteps }
