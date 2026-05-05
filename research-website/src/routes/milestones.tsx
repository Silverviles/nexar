import { createFileRoute } from "@tanstack/react-router";
import { CheckCircle2, Circle, Calendar, Award } from "lucide-react";
import { GlassCard } from "@/components/GlassCard";
import { Reveal } from "@/components/Reveal";
import { SectionHeader } from "@/components/SectionHeader";

export const Route = createFileRoute("/milestones")({
  head: () => ({
    meta: [
      { title: "Milestones — NEXAR" },
      { name: "description", content: "Project timeline: Proposal, Progress Presentations, Final Assessment, and Viva." },
      { property: "og:title", content: "Milestones — NEXAR" },
      { property: "og:description", content: "Track NEXAR research milestones from proposal to viva." },
    ],
  }),
  component: MilestonesPage,
});

const milestones = [
  { title: "Topic Evaluation", date: "TBD", marks: "TBD", status: "done", desc: "Initial evaluation of the research topic and problem statement." },
  { title: "Project Proposal (Presentation + Proposal Report)", date: "September 2025", marks: "TBD", status: "done", desc: "Formal proposal presentation and submission of the comprehensive report." },
  { title: "Progress Presentation I", date: "December 2025", marks: "TBD", status: "done", desc: "First demonstration of the foundational pipeline and system architecture." },
  { title: "Status Document I", date: "TBD", marks: "TBD", status: "done", desc: "Detailed documentation capturing current progress, blockers, and methodology updates." },
  { title: "Progress Presentation II", date: "March 2026", marks: "TBD", status: "done", desc: "Final comprehensive presentation of the fully functional system." },
  { title: "Research Paper", date: "April 2026", marks: "TBD", status: "done", desc: "Drafting and submission of the primary research paper to an academic conference or journal." },
  { title: "Status Document II", date: "May 2026", marks: "TBD", status: "done", desc: "Second official progress review document prior to final developments." },
  { title: "Final Reports (Thesis)", date: "May 2026", marks: "TBD", status: "pending", desc: "Complete dissertation combining all research, methodology, and results." },
  { title: "Final Evaluation", date: "May 2026", marks: "TBD", status: "pending", desc: "System evaluation and viva-voce with the examination panel." },
  { title: "Logbook Evaluation", date: "May 2026", marks: "TBD", status: "pending", desc: "Assessment of consistent progress logging throughout the project cycle." },
  { title: "Website Evaluation", date: "May 2026", marks: "TBD", status: "done", desc: "Evaluation of the project showcase website and public documentation." }
];

function statusStyles(status: string) {
  if (status === "done") return "border-primary/30 bg-primary/10 text-primary";
  if (status === "current") return "border-primary bg-primary text-primary-foreground";
  return "border-border bg-transparent text-muted-foreground";
}

function statusLabel(status: string) {
  if (status === "done") return "Completed";
  if (status === "current") return "In Progress";
  return "Upcoming";
}

function MilestonesPage() {
  return (
    <>
      <section className="border-b border-border">
        <div className="mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:px-8">
          <SectionHeader eyebrow="Timeline" title="Project Milestones." subtitle="Key checkpoints across the NEXAR research lifecycle." />
        </div>
      </section>

      <section className="mx-auto max-w-3xl px-6 py-20 lg:px-8">
        <div className="relative">
          <div className="absolute left-6 top-0 h-full w-px bg-border sm:left-8" />

          <div className="space-y-6">
            {milestones.map((m, i) => {
              const Icon = m.status === "done" ? CheckCircle2 : Circle;
              return (
                <Reveal key={m.title} delay={i * 0.06}>
                  <div className="relative pl-16 sm:pl-20">
                    <div className={`absolute left-0 top-2 flex h-12 w-12 items-center justify-center rounded-full border bg-background sm:h-16 sm:w-16 ${m.status === "done" ? "border-primary/50 text-primary" : m.status === "current" ? "border-primary text-primary shadow-[0_0_15px_rgba(var(--primary),0.3)]" : "border-border text-muted-foreground"}`}>
                      <Icon className={`h-5 w-5 sm:h-6 sm:w-6 ${m.status === "done" ? "text-primary" : m.status === "current" ? "text-primary" : "text-muted-foreground"}`} strokeWidth={m.status === "current" ? 2 : 1.5} />
                    </div>
                    <div className={`flex flex-col border-t-[3px] py-6 sm:py-8 transition-colors group ${m.status === "current" ? "border-primary" : "border-primary/20 hover:border-primary/50"}`}>
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <h3 className={`font-display text-xl font-semibold transition-colors ${m.status === "current" ? "text-foreground" : "text-foreground/90 group-hover:text-foreground"}`}>{m.title}</h3>
                          <div className="mt-2 text-primary flex flex-wrap items-center gap-4 text-xs">
                            <span className="inline-flex items-center gap-1.5 opacity-80"><Calendar className="h-3 w-3" />{m.date}</span>
                            <span className="inline-flex items-center gap-1.5 opacity-80"><Award className="h-3 w-3" />Weight: {m.marks}</span>
                          </div>
                        </div>
                        <span className={`rounded-full border px-3 py-1 mt-1 text-[11px] font-medium uppercase tracking-wider ${statusStyles(m.status)}`}>
                          {statusLabel(m.status)}
                        </span>
                      </div>
                      <p className="mt-4 text-[14.5px] leading-relaxed text-muted-foreground max-w-2xl">{m.desc}</p>
                    </div>
                  </div>
                </Reveal>
              );
            })}
          </div>
        </div>
      </section>
    </>
  );
}
