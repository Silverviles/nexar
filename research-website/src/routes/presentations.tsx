import { createFileRoute } from "@tanstack/react-router";
import { ExternalLink, Clock, ChevronRight } from "lucide-react";
import { Reveal } from "@/components/Reveal";
import { SectionHeader } from "@/components/SectionHeader";

export const Route = createFileRoute("/presentations")({
  head: () => ({
    meta: [
      { title: "Presentations — NEXAR" },
      { name: "description", content: "Slide decks for proposal, progress, and final NEXAR presentations." },
      { property: "og:title", content: "Presentations — NEXAR" },
      { property: "og:description", content: "Download or view NEXAR presentation decks." },
    ],
  }),
  component: PresentationsPage,
});

const decks = [
  {
    title: "Proposal Presentation",
    date: "Sep 2025",
    desc: "Initial presentation outlining the problem, research gap, and proposed approach.",
    viewUrl: "https://drive.google.com/file/d/1NglBZqhxeiRsYiIhWRTnZ_AiE654Zkhi/view?usp=sharing",
    embedUrl: "https://drive.google.com/file/d/1NglBZqhxeiRsYiIhWRTnZ_AiE654Zkhi/preview",
  },
  {
    title: "Progress Presentation 01",
    date: "Dec 2025",
    desc: "50% project completion — demonstrating early pipeline and routing model.",
    viewUrl: "https://drive.google.com/file/d/1r_ueUIVpfhJh2N1u6Df0O-UsSeExubAd/view?usp=sharing",
    embedUrl: "https://drive.google.com/file/d/1r_ueUIVpfhJh2N1u6Df0O-UsSeExubAd/preview",
  },
  {
    title: "Progress Presentation 02",
    date: "Mar 2026",
    desc: "90% project completion — full system integration and benchmark results.",
    viewUrl: "https://drive.google.com/file/d/1JV4AuNTvbo0f7Ux7_3OpQWDaA5rzIXWW/view?usp=sharing",
    embedUrl: "https://drive.google.com/file/d/1JV4AuNTvbo0f7Ux7_3OpQWDaA5rzIXWW/preview",
  },
  {
    title: "Final Presentation",
    date: "May 2026",
    desc: "100% completion with deployed solution and final evaluation.",
    viewUrl: "https://drive.google.com/file/d/1BB3lGJZ-4S57_rnNCJHFEIkyVs6VDasu/view?usp=sharing",
    embedUrl: "https://drive.google.com/file/d/1BB3lGJZ-4S57_rnNCJHFEIkyVs6VDasu/preview",
  },
];

function PresentationsPage() {
  return (
    <>
      <section className="border-b border-border">
        <div className="mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:px-8">
          <SectionHeader eyebrow="Decks" title="Presentations." subtitle="Slide decks delivered at each evaluation stage — previewed directly below." />
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-6 py-20 lg:px-8">
        <div className="space-y-16">
          {decks.map((d, i) => {
            const available = d.embedUrl !== null;
            return (
              <Reveal key={d.title} delay={i * 0.08}>
                <div className="group">
                  {/* Header */}
                  <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3 mb-5">
                    <div>
                      <span className="text-[12px] font-semibold uppercase tracking-widest text-primary mb-2 block">{d.date}</span>
                      <h3 className="font-display text-2xl font-semibold text-foreground">{d.title}</h3>
                      <p className="mt-1.5 text-[14.5px] leading-relaxed text-muted-foreground max-w-xl">{d.desc}</p>
                    </div>
                    {available && (
                      <a
                        href={d.viewUrl!}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 shrink-0 text-[13px] font-medium text-primary hover:underline underline-offset-4 transition-colors"
                      >
                        Open in Drive <ChevronRight className="h-3.5 w-3.5" />
                      </a>
                    )}
                  </div>

                  {/* Preview or Placeholder */}
                  {available ? (
                    <div className="rounded-xl overflow-hidden border border-border dark:border-white/10 shadow-lg dark:shadow-[0_8px_32px_rgba(0,0,0,0.4)] bg-black/5 dark:bg-white/[0.02]">
                      <iframe
                        src={d.embedUrl!}
                        className="w-full aspect-[16/9.5]"
                        allow="autoplay"
                        allowFullScreen
                        title={d.title}
                        style={{ border: 0 }}
                      />
                    </div>
                  ) : (
                    <div className="rounded-xl border border-dashed border-border dark:border-white/10 bg-muted/20 dark:bg-white/[0.02] flex flex-col items-center justify-center aspect-[16/6] gap-3">
                      <Clock className="h-8 w-8 text-muted-foreground/40" />
                      <span className="text-[14px] font-medium text-muted-foreground">Coming Soon</span>
                    </div>
                  )}
                </div>
              </Reveal>
            );
          })}
        </div>
      </section>
    </>
  );
}
