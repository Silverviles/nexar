import { createFileRoute } from "@tanstack/react-router";
import { FileText, Download, ExternalLink, CheckCircle2, Clock } from "lucide-react";
import { Reveal } from "@/components/Reveal";
import { SectionHeader } from "@/components/SectionHeader";

export const Route = createFileRoute("/documents")({
  head: () => ({
    meta: [
      { title: "Documents — NEXAR" },
      { name: "description", content: "Research documents, proposal, SRS, and dissertation downloads." },
      { property: "og:title", content: "Documents — NEXAR" },
      { property: "og:description", content: "Browse and download NEXAR research artifacts." },
    ],
  }),
  component: DocumentsPage,
});

const documents = [
  {
    name: "Topic Assessment Form",
    desc: "The document gives the information regarding the statement of scope, objectives overview, and people who are participating in a project.",
    type: "PDF",
    status: "Completed" as const,
    url: "https://drive.google.com/file/d/1KJZOpiy_9DNaGxpEEOiNqmh2C6hF1CBs/view?usp=sharing",
  },
  {
    name: "Project Proposal Reports",
    desc: "Documents containing details like goals, objectives, important dates, milestones and requirements needed to start and complete the project.",
    type: "PDF",
    status: "Completed" as const,
    url: "https://drive.google.com/drive/folders/1aRewQejX8dlLqovFp6WNish14BFWN2RC?usp=sharing",
  },
  {
    name: "Research Paper",
    desc: "A research paper containing Literature review, Research methodology, analysis, and argument based on in-depth independent research.",
    type: "PDF",
    status: "Completed" as const,
    url: "https://drive.google.com/drive/folders/1xKJtnAIoFxJh1nc9qdxZ8LiRW_kMB4i_?usp=sharing",
  },
  {
    name: "Final Thesis",
    desc: "The document contains the Proposed solution to the research question, which was finalized after completing the research.",
    type: "PDF",
    status: "Completed" as const,
    url: "https://drive.google.com/drive/folders/18eVZwQyVuG4c5-QKU7i_qXQwJ3yJTqKO?usp=sharing",
  },
  {
    name: "Status Document",
    desc: "The document describes the progress of the project within the specific time period and compares it against the project plan checklist.",
    type: "PDF",
    status: "Completed" as const,
    url: "https://drive.google.com/drive/folders/1ze1E8qy1ExyCgd--f9bvsmIoFp-kn2wa?usp=sharing",
  },
  {
    name: "Research Logbook",
    desc: "The document describes the progress of the project within the specific time period and compares it against the project plan checklist.",
    type: "PDF",
    status: "Completed" as const,
    url: "https://drive.google.com/drive/folders/1WVXb2e31IHKO35AUIuWT0jOVQwWvoFRp?usp=sharing",
  },
];

function DocumentsPage() {
  return (
    <>
      <section className="border-b border-border">
        <div className="mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:px-8">
          <SectionHeader eyebrow="Library" title="Research Documents." subtitle="All written artifacts produced throughout the project." />
        </div>
      </section>

      <section className="mx-auto max-w-4xl px-6 py-20 lg:px-8">
        <div className="grid gap-4">
          {documents.map((d, i) => (
            <Reveal key={d.name} delay={i * 0.04}>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 border border-border dark:border-white/10 bg-surface/50 dark:bg-white/[0.03] rounded-xl transition-all hover:border-primary/40 group">
                <div className="flex items-start gap-4 min-w-0">
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary/10 dark:bg-primary/15 border border-primary/20">
                    <FileText className="h-5 w-5 text-primary" strokeWidth={1.6} />
                  </div>
                  <div className="min-w-0">
                    <h3 className="font-display text-base font-semibold group-hover:text-primary transition-colors">{d.name}</h3>
                    <p className="mt-1 text-[13px] leading-relaxed text-muted-foreground line-clamp-2">{d.desc}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2.5 shrink-0 sm:ml-4">
                  <span className="inline-flex items-center gap-1.5 rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-[11px] font-medium text-primary">
                    <CheckCircle2 className="h-3 w-3" />
                    {d.status}
                  </span>
                  <a
                    href={d.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label={`View ${d.name}`}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-border dark:border-white/10 px-3 py-2 text-[13px] font-medium text-muted-foreground transition-colors hover:bg-primary/10 hover:text-primary hover:border-primary/30"
                  >
                    <ExternalLink className="h-3.5 w-3.5" />
                    View
                  </a>
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </section>
    </>
  );
}
