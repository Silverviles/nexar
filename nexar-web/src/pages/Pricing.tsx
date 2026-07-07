import { Link } from 'react-router-dom'
import { Check, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { FadeIn } from '@/components/ui/FadeIn'
import { Section } from '@/components/ui/Section'
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table'
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from '@/components/ui/Accordion'
import { MarketingLayout } from '@/components/layout/MarketingLayout'
import { PRICING_TIERS } from '@/lib/marketing-content'

const COMPARISON_ROWS = [
  { label: 'Analyses / month', values: ['50', '2,000', 'Unlimited'] },
  { label: 'Hardware providers', values: ['Qiskit simulator', 'Qiskit + Braket + Azure', 'All providers + dedicated'] },
  { label: 'Decision rationale & cost estimates', values: ['Basic', 'Full detail', 'Full detail'] },
  { label: 'Support', values: ['Community', 'Priority email', 'Dedicated + SLA'] },
]

const PRICING_FAQS = [
  {
    question: 'Can I switch plans at any time?',
    answer: 'Yes. Upgrades apply immediately, and downgrades take effect at the start of your next billing cycle.',
  },
  {
    question: 'What happens if I go over my monthly analyses?',
    answer:
      'On Free and Pro, additional analyses are billed at a per-analysis overage rate rather than being blocked outright.',
  },
  {
    question: 'Is there a free trial for Pro?',
    answer: 'Pro includes a 14-day free trial — no credit card required to start.',
  },
  {
    question: 'Do Enterprise plans include dedicated hardware?',
    answer:
      'Yes. Enterprise plans can reserve dedicated capacity on your chosen provider in addition to on-demand access to all three.',
  },
]

function Pricing() {
  return (
    <MarketingLayout>
      {/* Hero */}
      <section className="container mx-auto px-6 py-24 md:py-32 text-center">
        <FadeIn>
          <div className="inline-flex items-center gap-2 border border-primary/30 bg-surface-1 px-4 py-2 text-sm font-medium text-primary mb-8">
            <Sparkles className="h-4 w-4" />
            Pricing
          </div>
          <h1 className="text-5xl md:text-[76px] font-light leading-[1.17] tracking-[-0.5px] text-ink mb-6 max-w-4xl mx-auto">
            Straightforward plans for every workload
          </h1>
          <p className="text-lg text-ink-muted mb-10 max-w-2xl mx-auto leading-relaxed">
            Start free. Scale to dedicated hardware and support when you need it.
          </p>
        </FadeIn>
      </section>

      {/* Tiers */}
      <section className="container mx-auto px-6 py-20">
        <div className="grid md:grid-cols-3 gap-px bg-hairline max-w-6xl mx-auto border border-hairline">
          {PRICING_TIERS.map((tier, i) => (
            <FadeIn key={tier.name} delay={i * 0.05} inView>
              <Card variant={tier.highlight ? 'quantum' : 'default'} className="h-full border-0 relative">
                <CardContent className="p-8 flex flex-col h-full">
                  {tier.highlight && (
                    <Badge variant="quantum" className="absolute right-6 top-6">
                      Most popular
                    </Badge>
                  )}
                  <h3 className="text-xl font-normal mb-1 text-ink">{tier.name}</h3>
                  <p className="text-sm text-ink-muted mb-4">{tier.description}</p>
                  <div className="mb-6">
                    <span className="text-3xl font-light text-ink">{tier.price}</span>
                    <span className="text-ink-muted">{tier.period}</span>
                  </div>
                  <ul className="space-y-3 text-sm text-ink-muted mb-8 flex-1">
                    {tier.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-2">
                        <Check className="h-4 w-4 text-success shrink-0 mt-0.5" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                  <Link to={tier.href}>
                    <Button className="w-full" variant={tier.highlight ? 'default' : 'outline'}>
                      {tier.cta}
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            </FadeIn>
          ))}
        </div>
      </section>

      {/* Comparison table */}
      <Section tone="surface">
        <FadeIn inView className="text-center mb-12">
          <h2 className="text-3xl md:text-[42px] font-light text-ink mb-4">Compare Plans</h2>
        </FadeIn>
        <FadeIn inView className="max-w-4xl mx-auto border border-hairline bg-canvas">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Feature</TableHead>
                {PRICING_TIERS.map((tier) => (
                  <TableHead key={tier.name}>{tier.name}</TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {COMPARISON_ROWS.map((row) => (
                <TableRow key={row.label}>
                  <TableCell className="font-medium">{row.label}</TableCell>
                  {row.values.map((value, i) => (
                    <TableCell key={PRICING_TIERS[i].name}>{value}</TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </FadeIn>
      </Section>

      {/* Pricing FAQ */}
      <section className="container mx-auto px-6 py-20">
        <FadeIn inView className="text-center mb-16">
          <h2 className="text-3xl md:text-[42px] font-light text-ink mb-4">Billing Questions</h2>
        </FadeIn>
        <FadeIn inView className="max-w-3xl mx-auto">
          <Accordion defaultValue={PRICING_FAQS[0].question}>
            {PRICING_FAQS.map((faq) => (
              <AccordionItem key={faq.question} value={faq.question}>
                <AccordionTrigger>{faq.question}</AccordionTrigger>
                <AccordionContent>{faq.answer}</AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </FadeIn>
      </section>
    </MarketingLayout>
  )
}

export default Pricing
