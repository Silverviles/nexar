import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Mail, MapPin, Github, Send, ArrowRight } from "lucide-react";
import { toast } from "sonner";
import { Reveal } from "@/components/Reveal";
import { SectionHeader } from "@/components/SectionHeader";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { SOCIAL_LINKS } from "@/config/social.config";

export const Route = createFileRoute("/contact")({
  head: () => ({
    meta: [
      { title: "Contact — NEXAR" },
      { name: "description", content: "Get in touch with the NEXAR research team." },
      { property: "og:title", content: "Contact — NEXAR" },
      { property: "og:description", content: "Reach the NEXAR team for questions and collaboration." },
    ],
  }),
  component: ContactPage,
});

function ContactPage() {
  const [submitting, setSubmitting] = useState(false);

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSubmitting(true);
    setTimeout(() => {
      toast.success("Message received", { description: "We'll get back to you shortly." });
      (e.target as HTMLFormElement).reset();
      setSubmitting(false);
    }, 700);
  };

  return (
    <>
      <section className="border-b border-border relative overflow-hidden">
        {/* Subtle background glow for the header */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] opacity-10 pointer-events-none">
          <div className="absolute inset-0 bg-primary/40 blur-[100px] rounded-full mix-blend-screen" />
        </div>
        <div className="mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:px-8 relative z-10">
          <SectionHeader 
            eyebrow="Get in touch" 
            title="Let's talk research." 
            subtitle="Questions, collaboration ideas, or feedback — we're listening." 
          />
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 py-20 lg:px-8">
        <div className="grid gap-8 lg:grid-cols-[1fr_1.4fr]">
          
          <Reveal>
            <div className="h-full border border-border dark:border-white/10 bg-surface/50 dark:bg-white/[0.02] rounded-2xl p-8 sm:p-10 shadow-sm dark:shadow-[0_8px_32px_rgba(0,0,0,0.2)]">
              <h3 className="font-display text-2xl font-semibold">Contact details</h3>
              <p className="mt-2 text-[15px] text-muted-foreground">Reach us through any of the channels below.</p>
              
              <ul className="mt-10 space-y-8">
                <li className="group flex items-start gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10 dark:bg-primary/20 border border-primary/20 transition-transform duration-300 group-hover:scale-105">
                    <Mail className="h-5 w-5 text-primary" strokeWidth={1.5} />
                  </div>
                  <div className="min-w-0">
                    <div className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground mb-1">Email</div>
                    <a href={`mailto:${SOCIAL_LINKS.EMAIL}`} className="text-[15px] font-medium text-foreground hover:text-primary transition-colors flex items-center gap-2">
                      {SOCIAL_LINKS.EMAIL} <ArrowRight className="h-3.5 w-3.5 opacity-0 -translate-x-2 transition-all group-hover:opacity-100 group-hover:translate-x-0" />
                    </a>
                  </div>
                </li>
                
                <li className="group flex items-start gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10 dark:bg-primary/20 border border-primary/20 transition-transform duration-300 group-hover:scale-105">
                    <Github className="h-5 w-5 text-primary" strokeWidth={1.5} />
                  </div>
                  <div className="min-w-0">
                    <div className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground mb-1">GitHub</div>
                    <a href={SOCIAL_LINKS.GITHUB} target="_blank" rel="noopener noreferrer" className="text-[15px] font-medium text-foreground hover:text-primary transition-colors flex items-center gap-2 truncate">
                      Silverviles/nexar <ArrowRight className="h-3.5 w-3.5 opacity-0 -translate-x-2 transition-all group-hover:opacity-100 group-hover:translate-x-0" />
                    </a>
                  </div>
                </li>
                
                <li className="group flex items-start gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10 dark:bg-primary/20 border border-primary/20 transition-transform duration-300 group-hover:scale-105">
                    <MapPin className="h-5 w-5 text-primary" strokeWidth={1.5} />
                  </div>
                  <div className="min-w-0">
                    <div className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground mb-1">Address</div>
                    <span className="text-[15px] font-medium text-foreground block mt-0.5">
                      Faculty of Computing<br/>SLIIT, Malabe
                    </span>
                  </div>
                </li>
              </ul>
            </div>
          </Reveal>

          <Reveal delay={0.08}>
            <div className="border border-border dark:border-white/10 bg-surface/50 dark:bg-white/[0.02] rounded-2xl p-8 sm:p-10 shadow-sm dark:shadow-[0_8px_32px_rgba(0,0,0,0.2)]">
              <form onSubmit={onSubmit} className="space-y-6">
                <div className="grid gap-6 sm:grid-cols-2">
                  <div className="space-y-2.5">
                    <Label htmlFor="name" className="text-muted-foreground">Name</Label>
                    <Input id="name" name="name" required placeholder="Your name" className="bg-background dark:bg-black/20" />
                  </div>
                  <div className="space-y-2.5">
                    <Label htmlFor="email" className="text-muted-foreground">Email</Label>
                    <Input id="email" name="email" type="email" required placeholder="you@example.com" className="bg-background dark:bg-black/20" />
                  </div>
                </div>
                <div className="space-y-2.5">
                  <Label htmlFor="message" className="text-muted-foreground">Message</Label>
                  <Textarea id="message" name="message" required rows={6} placeholder="Tell us about your inquiry…" className="bg-background dark:bg-black/20 resize-none" />
                </div>
                
                <div className="pt-2">
                  <button
                    type="submit"
                    disabled={submitting}
                    className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-6 py-3.5 text-sm font-medium text-primary-foreground transition-all hover:bg-primary/90 hover:shadow-lg disabled:opacity-60"
                  >
                    <Send className="h-4 w-4" />
                    {submitting ? "Sending…" : "Send message"}
                  </button>
                </div>
              </form>
            </div>
          </Reveal>

        </div>
      </section>
    </>
  );
}
