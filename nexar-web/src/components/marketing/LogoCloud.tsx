import { FadeIn } from '@/components/ui/FadeIn'

const PARTNERS = ['Quantalytics', 'Northwind Labs', 'Orbit Dynamics', 'Vantage Systems', 'Helios Cloud', 'Meridian AI']

function LogoCloud() {
  return (
    <section className="border-y border-hairline bg-surface-1 py-12">
      <div className="container mx-auto px-6">
        <FadeIn inView className="mb-8 text-center text-xs font-medium uppercase tracking-widest text-ink-subtle">
          Trusted by teams building the next generation of compute
        </FadeIn>
        <FadeIn inView className="flex flex-wrap items-center justify-center gap-x-12 gap-y-6">
          {PARTNERS.map((name) => (
            <span key={name} className="font-mono text-lg text-ink-subtle transition-colors hover:text-ink">
              {name}
            </span>
          ))}
        </FadeIn>
      </div>
    </section>
  )
}

export { LogoCloud }
