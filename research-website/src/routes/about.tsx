import { createFileRoute } from "@tanstack/react-router";
import {
  Users,
  BookOpen,
  Sparkles,
  Workflow,
  FileCode2,
  BrainCircuit,
  GitFork,
  Cpu,
  ExternalLink,
} from "lucide-react";
import { Reveal } from "@/components/Reveal";
import { SectionHeader } from "@/components/SectionHeader";


import imgSiriwardhana from "../assets/about/member-siriwardhana.jpeg";
import imgPrasad from "../assets/about/member-prasad.png";
import imgJayasinghe from "../assets/about/member-jayasinghe.jpeg";
import imgHettiarachchi from "../assets/about/member-hettiarachchi.png";
import imgNuwan from "../assets/about/member-nuwan-prof.png";
import imgKapila from "../assets/about/member-kapila-dr.png";

export const Route = createFileRoute("/about")({
  head: () => ({
    meta: [
      { title: "About — NEXAR" },
      {
        name: "description",
        content: "The story behind NEXAR, the research team, and our motivations.",
      },
      { property: "og:title", content: "About — NEXAR" },
      { property: "og:description", content: "Learn about the researchers and research driving NEXAR forward." },
    ],
  }),
  component: AboutPage,
});

const projectHighlights = [
  { title: "Code Analysis Engine (CAE)", desc: "Parses code across five frameworks, extracting 16-feature vectors describing complexity, entanglement, and NISQ viability.", icon: FileCode2 },
  { title: "AI Code Converter (ACC)", desc: "Uses a fine-tuned CodeT5 model to seamlessly translate classical Python algorithms into Qiskit quantum circuits.", icon: BrainCircuit },
  { title: "Decision Engine (DE)", desc: "Combines ML ensembles (50%), physics rules (35%), and cost analysis (15%) to produce intelligent routing paths.", icon: GitFork },
  { title: "Hardware Abstraction (HAL)", desc: "A unified API routing workloads seamlessly into IBM Quantum, AWS Braket, and Azure Quantum.", icon: Cpu }
];

const supervisors = [
  { name: "Prof. Nuwan Kodagoda", role: "Supervisor", department: "Department of Information Technology, SLIIT", img: imgNuwan , contactUrl: "https://www.linkedin.com/in/nuwan-kodagoda-a4875a4"},
  { name: "Dr. Kapila Dissanayaka", role: "Co-Supervisor", department: "Department of Computer Science and Software Engineering, SLIIT", img: imgKapila , contactUrl: "https://www.sliit.lk/academic/academic-staff/kapila.d"},
];

const team = [
  { name: "Siriwardhana A. H. L. T. S.", alias: "Sudaraka Tharindu", id: "IT22094568", role: "Hardware Abstraction Layer", img: imgSiriwardhana , contactUrl: "https://www.linkedin.com/in/tharindu-siriwardhana" },
  { name: "Prasad H. G. A. T.", alias: "Ashan Tharindu", id: "IT22056870", role: "Decision Engine", img: imgPrasad, contactUrl: "https://www.linkedin.com/in/ashan-tharindu" },
  { name: "Jayasinghe Y. L.", alias: "Yashodha Lasith", id: "IT22103840", role: "Code Analysis Engine", img: imgJayasinghe , contactUrl :"https://www.linkedin.com/in/yashodha-jayasinghe-1104122a3"},
  { name: "Hettiarachchi S. R.", alias: "Sayun Hettiarachchi", id: "IT22128386", role: "AI Code Converter", img: imgHettiarachchi, contactUrl: "https://www.linkedin.com/in/sayun-hettiarachchi-37b14a2a6" },
];

const contributions = [
  { title: "Automated Code Analysis Pipeline", desc: "A multi-dimensional engine extracting features via CodeBERT, ensemble ML, and pattern matching." },
  { title: "Hybrid Decision Framework", desc: "The first system to unify ML predictions, physics rules, and cost analysis via calibrated weighted voting." },
  { title: "Provider-Agnostic Execution", desc: "A robust hardware abstraction layer unifying major quantum cloud providers behind a single API." },
  { title: "Empirical Evaluation", desc: "A benchmark of 100 workloads revealing the quantum-classical crossover at ~50–57 qubits." },
];

function AboutPage() {
  return (
    <>
      <section className="border-b border-border">
        <div className="mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:px-8">
          <SectionHeader 
            eyebrow="Platform & People" 
            title="The story behind NEXAR." 
            subtitle="An undergraduate research project automating the divide between quantum and classical infrastructure." 
          />
        </div>
      </section>

      <section className="mx-auto max-w-4xl px-6 py-20 lg:px-8 space-y-32">
        <Reveal>
          <div>
            <h2 className="font-display text-3xl font-semibold mb-6 flex items-center gap-3">
              <Workflow className="h-6 w-6 text-primary"/> About the Project
            </h2>
            <div className="prose prose-zinc dark:prose-invert max-w-none text-muted-foreground leading-relaxed text-[16px]">
              <p>
                <strong className="text-foreground">Nexar</strong> (internally project RP 25-26J-484, also known as the <strong className="text-foreground">Quantum-Classical Code Router</strong> / QCCR) is a full-stack platform that automates the analysis, classification, and routing of computational workloads across quantum and classical execution backends.
              </p>
              <p className="mt-4">
                Given a piece of source code, Nexar answers a deceptively simple question: <em>should this run on classical hardware, a quantum simulator, or a real quantum device — and at what cost?</em> Behind that answer sits a pipeline of four tightly-integrated components:
              </p>
            </div>
            
            <div className="grid gap-6 sm:grid-cols-2 mt-10">
              {projectHighlights.map((hl, i) => (
                <div key={i} className="flex flex-col border-t-[3px] border-primary/20 pt-5 transition-colors hover:border-primary group bg-transparent">
                  <h3 className="font-display text-lg font-semibold group-hover:text-primary transition-colors flex gap-2.5 items-center">
                    <hl.icon className="h-4.5 w-4.5 text-primary/70 group-hover:text-primary"/>
                    {hl.title}
                  </h3>
                  <p className="mt-3 text-[14.5px] leading-relaxed text-muted-foreground">
                    {hl.desc}
                  </p>
                </div>
              ))}
            </div>
            
            <p className="text-[16px] leading-relaxed text-muted-foreground mt-10">
              The platform has been evaluated across 100 diverse workloads spanning classical computation, hybrid quantum-classical algorithms, and pure quantum circuits — achieving correct routing decisions across all categories with an average pipeline latency of 1.5 seconds and decision inference under 15 ms.
            </p>
          </div>
        </Reveal>

        <Reveal delay={0.1}>
          <div>
            <h2 className="font-display text-3xl font-semibold mb-6 flex items-center gap-3">
              <Users className="h-6 w-6 text-primary"/> About the Team
            </h2>
            <p className="text-[16px] leading-relaxed text-muted-foreground mb-12">
              Nexar is built by a team of four undergraduate researchers from the <strong className="text-foreground">Sri Lanka Institute of Information Technology (SLIIT)</strong>, guided by our supervisors. All team members are pursuing a B.Sc. (Hons) in Information Technology specializing in Software Engineering.
            </p>

            <h3 className="font-display text-2xl font-semibold mb-6 text-foreground border-b border-border pb-3">Supervisors</h3>
            <div className="grid gap-6 sm:grid-cols-2 mb-16">
              {supervisors.map((s, i) => (
                <div key={i} className="flex gap-5 border border-border/50 bg-background/50 p-5 transition-all hover:border-primary/50 group rounded-xl">
                  <div className="h-20 w-20 shrink-0 overflow-hidden rounded-xl border border-primary/20">
                    <img src={s.img} alt={s.name} className="h-full w-full object-cover transition-transform group-hover:scale-105" />
                  </div>
                  <div className="flex flex-col justify-center">
                    <div className="flex items-center gap-2">
                      <h4 className="font-display text-[17px] font-semibold group-hover:text-primary transition-colors">{s.name}</h4>
                      <a href={s.contactUrl} target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-primary transition-colors shrink-0" aria-label={`Contact ${s.name}`}>
                        <ExternalLink className="h-3.5 w-3.5" />
                      </a>
                    </div>
                    <span className="text-[13px] font-medium text-primary mb-1.5">{s.role}</span>
                    <p className="text-[13px] text-muted-foreground leading-relaxed pr-2">{s.department}</p>
                  </div>
                </div>
              ))}
            </div>

            <h3 className="font-display text-2xl font-semibold mb-6 text-foreground border-b border-border pb-3">Research Team</h3>
            <div className="grid gap-6 sm:grid-cols-2">
              {team.map((m, i) => (
                <div key={i} className="flex gap-5 border border-border/50 bg-background/50 p-5 transition-all hover:border-primary/50 group rounded-xl">
                  <div className="h-24 w-24 shrink-0 overflow-hidden border border-primary/20 rounded-xl relative shadow-sm">
                    <img src={m.img} alt={m.name} className="h-full w-full object-cover transition-transform group-hover:scale-105" />
                  </div>
                  <div className="flex flex-col justify-center">
                    <div className="flex items-center gap-2">
                      <h4 className="font-display text-[17px] font-semibold group-hover:text-primary transition-colors">{m.name}</h4>
                      <a href={m.contactUrl} target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-primary transition-colors shrink-0" aria-label={`Contact ${m.name}`}>
                        <ExternalLink className="h-3.5 w-3.5" />
                      </a>
                    </div>
                    <span className="text-[12.5px] text-muted-foreground mb-3">{m.alias} <span className="opacity-50 mx-1">|</span> {m.id}</span>
                    <span className="inline-flex max-w-fit items-center rounded-md bg-primary/10 px-2.5 py-1 text-[11.5px] font-medium text-primary border border-primary/20">
                      {m.role}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Reveal>

        <Reveal delay={0.2}>
          <div>
            <h2 className="font-display text-3xl font-semibold mb-6 flex items-center gap-3">
              <BookOpen className="h-6 w-6 text-primary"/> About the Research
            </h2>
            <div className="prose prose-zinc dark:prose-invert max-w-none text-[16px] leading-relaxed text-muted-foreground mb-10">
              <p>
                Nexar is an undergraduate dissertation research project (<strong className="text-foreground">RP 25-26J-484</strong>) positioned at the intersection of quantum computing, machine learning, and cloud infrastructure.
              </p>
              <p className="mt-4">
                The project runs for one academic year and produces multiple deliverables including individual component dissertations, a consolidated research paper, open-source implementation, and this research website. The team collaborates with faculty research groups in quantum software engineering and draws on SLIIT's high-performance computing infrastructure for model training and benchmarking.
              </p>
            </div>

            <h3 className="font-display text-xl font-semibold mb-5 text-foreground/90">Core Contributions</h3>
            <ul className="space-y-4">
              {contributions.map((c, i) => (
                <li key={i} className="flex gap-4">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/40 border border-primary/20" />
                  <p className="text-[14.5px] leading-relaxed text-muted-foreground">
                    <strong className="font-medium text-foreground">{c.title}</strong> — {c.desc}
                  </p>
                </li>
              ))}
            </ul>
          </div>
        </Reveal>

        <Reveal delay={0.3}>
          <div>
            <h2 className="font-display text-3xl font-semibold mb-6 flex items-center gap-3">
              <Sparkles className="h-6 w-6 text-primary"/> Our Motivation
            </h2>
            <div className="bg-primary/5 border-l-4 border-primary p-6 sm:p-8 rounded-r-xl">
              <p className="text-[16px] leading-relaxed text-foreground italic">
                "Quantum computing has moved from the lab into the cloud. IBM, AWS, and Microsoft now offer public access to real quantum processors with tens to hundreds of qubits — yet for most developers, a question still looms: does my code actually belong on a quantum computer, and can I afford to run it there?"
              </p>
            </div>
            <p className="text-[16px] leading-relaxed text-muted-foreground mt-8">
              Today, answering that question is hard. It requires deep expertise in quantum algorithms, intimate knowledge of NISQ-era hardware noise, and constant tracking of rapidly-changing provider pricing. The overhead of transpilation, measurement shots, queue times, and error rates means that for many problems — especially those with polynomial classical solutions — classical execution remains orders of magnitude faster and cheaper. 
            </p>
            <p className="text-[16px] leading-relaxed text-muted-foreground mt-4">
              Our mission with Nexar is to abstract away that complexity, democratizing access to hybrid computation by making intelligent routing autonomous and effortless.
            </p>
          </div>
        </Reveal>
      </section>
    </>
  );
}
