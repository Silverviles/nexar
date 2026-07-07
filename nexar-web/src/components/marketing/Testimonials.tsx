import { Card, CardContent } from '@/components/ui/card'
import { FadeIn } from '@/components/ui/FadeIn'
import { Quote } from 'lucide-react'

const TESTIMONIALS = [
  {
    quote:
      "Nexar's routing engine cut our simulation costs by a third in the first month — we stopped guessing which workloads needed quantum hardware.",
    name: 'Dr. Elena Ross',
    role: 'Quantum Research Lead, Northwind Labs',
  },
  {
    quote:
      'The decision engine caught patterns in our optimization pipeline our own team had missed. It reads like an extra senior engineer on the team.',
    name: 'Marcus Webb',
    role: 'Head of Platform, Orbit Dynamics',
  },
  {
    quote:
      'We went from manually deciding hardware per job to trusting the confidence score outright. Execution history made the case for leadership.',
    name: 'Priya Nandan',
    role: 'VP Engineering, Vantage Systems',
  },
]

function Testimonials() {
  return (
    <section className="container mx-auto px-6 py-20">
      <FadeIn inView className="text-center mb-16">
        <h2 className="text-3xl md:text-[42px] font-light text-ink mb-4">What Teams Are Saying</h2>
        <p className="text-ink-muted max-w-2xl mx-auto">Early feedback from teams piloting Nexar in production</p>
      </FadeIn>

      <div className="grid md:grid-cols-3 gap-px bg-hairline max-w-6xl mx-auto border border-hairline">
        {TESTIMONIALS.map((t, i) => (
          <FadeIn key={t.name} delay={i * 0.05} inView>
            <Card className="h-full border-0 hover:bg-surface-1">
              <CardContent className="flex h-full flex-col p-8">
                <Quote className="h-6 w-6 text-primary mb-4" />
                <p className="mb-6 flex-1 text-sm leading-relaxed text-ink-muted">&ldquo;{t.quote}&rdquo;</p>
                <div>
                  <p className="text-sm font-medium text-ink">{t.name}</p>
                  <p className="text-xs text-ink-subtle">{t.role}</p>
                </div>
              </CardContent>
            </Card>
          </FadeIn>
        ))}
      </div>
    </section>
  )
}

export { Testimonials }
