import { FadeIn } from '@/components/ui/FadeIn'
import { Section } from '@/components/ui/Section'
import { HARDWARE_PROVIDERS } from '@/lib/marketing-content'

function HardwareBand() {
  return (
    <Section tone="surface">
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-[42px] font-light text-ink mb-4">Real Quantum Hardware, One Interface</h2>
        <p className="text-ink-muted max-w-2xl mx-auto">
          Nexar routes to real providers — not just simulators
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto text-center">
        {HARDWARE_PROVIDERS.map((provider, i) => (
          <FadeIn key={provider.name} delay={i * 0.05} inView>
            <h3 className="text-lg font-normal text-ink mb-2">{provider.name}</h3>
            <p className="text-ink-muted text-sm">{provider.description}</p>
          </FadeIn>
        ))}
      </div>
    </Section>
  )
}

export { HardwareBand }
