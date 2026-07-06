import { useState, type FormEvent } from 'react'
import { Mail, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { FadeIn } from '@/components/ui/FadeIn'
import { MarketingLayout } from '@/components/layout/MarketingLayout'
import { toast } from '@/components/ui/sonner'

function Contact() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    toast.success("Message sent — we'll get back to you soon.")
    setName('')
    setEmail('')
    setMessage('')
  }

  return (
    <MarketingLayout>
      <section className="container mx-auto px-6 py-24 md:py-32 text-center">
        <FadeIn>
          <div className="inline-flex items-center gap-2 border border-primary/30 bg-surface-1 px-4 py-2 text-sm font-medium text-primary mb-8">
            <Sparkles className="h-4 w-4" />
            Contact
          </div>
          <h1 className="text-5xl md:text-[76px] font-light leading-[1.17] tracking-[-0.5px] text-ink mb-6 max-w-4xl mx-auto">
            Get in touch
          </h1>
          <p className="text-lg text-ink-muted mb-10 max-w-2xl mx-auto leading-relaxed">
            Questions about the platform, enterprise plans, or the API? We'd like to hear from you.
          </p>
        </FadeIn>
      </section>

      <section className="container mx-auto px-6 pb-24">
        <div className="grid md:grid-cols-2 gap-12 max-w-4xl mx-auto">
          <FadeIn>
            <h2 className="text-xl font-normal text-ink mb-4">Contact info</h2>
            <a
              href="mailto:hello@nexar.dev"
              className="inline-flex items-center gap-2 text-primary hover:underline mb-6"
            >
              <Mail className="h-4 w-4" />
              hello@nexar.dev
            </a>
            <p className="text-ink-muted text-sm leading-relaxed">
              For enterprise pricing or API access questions, use the form or email us directly — we typically
              respond within one business day.
            </p>
          </FadeIn>

          <FadeIn delay={0.05}>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="name">Name</Label>
                <Input id="name" value={name} onChange={(e) => setName(e.target.value)} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="message">Message</Label>
                <Textarea
                  id="message"
                  rows={5}
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  required
                />
              </div>
              <Button type="submit" className="w-full">
                Send message
              </Button>
            </form>
          </FadeIn>
        </div>
      </section>
    </MarketingLayout>
  )
}

export default Contact
