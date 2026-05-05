import { createFileRoute, Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { ArrowRight, Cpu, GitBranch, Zap, Network } from "lucide-react";
import { GlassCard } from "@/components/GlassCard";
import { Reveal } from "@/components/Reveal";
import { SectionHeader } from "@/components/SectionHeader";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "NEXAR — Quantum Classical Code Router" },
      { name: "description", content: "Intelligently route code between quantum and classical compute targets to maximize performance and accuracy." },
      { property: "og:title", content: "NEXAR — Quantum Classical Code Router" },
      { property: "og:description", content: "A research initiative on hybrid quantum-classical execution routing." },
    ],
  }),
  component: Home,
});

const highlights = [
  { icon: Cpu, title: "Code Analysis Engine", desc: "Extracts 16-feature vectors across 5 frameworks via CodeBERT and AST pattern matching." },
  { icon: GitBranch, title: "AI Code Conversion", desc: "Fine-tuned CodeT5 models seamlessly translating classical Python into optimized Qiskit circuits." },
  { icon: Zap, title: "Decision Engine", desc: "Fusing ML ensembles, physics rules, and real-time cost estimators for calibrated routing." },
  { icon: Network, title: "Hardware Abstraction", desc: "Abstracting IBM Quantum, AWS Braket, and Azure Quantum behind a single unified API." },
];

const stats = [
  { value: "4", label: "Core Microservices" },
  { value: "100", label: "Evaluated Workloads" },
  { value: "50-57", label: "Qubit Cost Crossover" },
  { value: "<15ms", label: "Decision Inference Latency" },
];

function Home() {
  return (
    <>
      {/* Hero */}
      <section className="relative overflow-hidden bg-background">
        {/* Abstract Dark Mode Background Elements */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] opacity-20 pointer-events-none">
          <div className="absolute inset-0 bg-primary/40 blur-[120px] rounded-full mix-blend-screen animate-in fade-in duration-1000" />
        </div>

        <div className="relative mx-auto max-w-5xl px-6 pb-24 pt-32 text-center sm:pt-40 lg:px-8 lg:pt-48">
          <motion.div
            initial={{ opacity: 0, y: 15, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            className="mb-8 inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-4 py-1.5 text-[13px] font-semibold tracking-wide text-primary shadow-[0_0_20px_rgba(var(--primary),0.15)] backdrop-blur-md"
          >
            <Zap className="h-3.5 w-3.5" /> Research Project · 2025
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, delay: 0.05, ease: [0.22, 1, 0.36, 1] }}
            className="font-display text-5xl font-semibold leading-[1.05] tracking-tight text-foreground sm:text-6xl lg:text-7xl"
          >
            Quantum classical
            <br />
            <span className="text-muted-foreground">code router</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, delay: 0.15, ease: [0.22, 1, 0.36, 1] }}
            className="mx-auto mt-8 max-w-2xl text-[17px] leading-relaxed text-muted-foreground font-medium"
          >
            NEXAR analyzes program structure and runtime characteristics to intelligently route
            code segments between quantum processors and classical CPUs — unlocking the practical
            potential of hybrid computing.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.25 }}
            className="mt-10 flex flex-wrap justify-center gap-3"
          >
            <Link
              to="/domain"
              className="inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
            >
              View Research
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              to="/domain"
              className="inline-flex items-center gap-2 rounded-full border border-border bg-surface-elevated px-6 py-3 text-sm font-medium text-foreground transition-colors hover:bg-muted"
            >
              Explore Domain
            </Link>
          </motion.div>

          {/* Visual */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.35, ease: [0.22, 1, 0.36, 1] }}
            className="mx-auto mt-20 max-w-4xl"
          >
            <div className="border border-border dark:border-white/10 bg-surface/50 dark:bg-background/40 backdrop-blur-md rounded-2xl overflow-hidden shadow-lg dark:shadow-[0_8px_32px_rgba(0,0,0,0.4)]">
              <div className="grid grid-cols-2 divide-x divide-border dark:divide-white/10">
                <div className="p-10 text-left hover:bg-primary/5 transition-colors">
                  <div className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Classical Evaluator</div>
                  <div className="mt-3 font-display text-2xl font-semibold">Classical CPU</div>
                  <p className="mt-2 text-[14px] leading-relaxed text-muted-foreground">Local or cloud-provisioned runtimes for sequential and deterministically fast polynomial workloads.</p>
                </div>
                <div className="p-10 text-left hover:bg-primary/5 transition-colors">
                  <div className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Quantum Evaluator</div>
                  <div className="mt-3 font-display text-2xl font-semibold">QPU Backend</div>
                  <p className="mt-2 text-[14px] leading-relaxed text-muted-foreground">IBM Quantum / Braket / Azure targets reserved for algorithmically advantageous chemistry and combinatorial tasks.</p>
                </div>
              </div>
              <div className="border-t border-border dark:border-white/10 bg-muted/50 dark:bg-white/5 px-10 py-5">
                <div className="flex items-center justify-between text-[13px]">
                  <span className="font-mono text-primary font-medium tracking-wide">nexar_pipeline.evaluate(workload)</span>
                  <span className="font-medium text-muted-foreground dark:text-white/80">{'<'} 15ms inference</span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Highlights */}
      <section className="mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:px-8 relative z-10">
        <SectionHeader
          eyebrow="Capabilities"
          title="A new layer for hybrid compute."
          subtitle="NEXAR sits seamlessly between developer code and execution backends, autonomously deciding what runs where."
        />
        <div className="mt-16 grid gap-px border border-border bg-border sm:grid-cols-2 lg:grid-cols-2">
          {highlights.map((h, i) => (
            <Reveal key={h.title} delay={i * 0.06}>
              <div className="h-full bg-background p-10 hover:bg-primary/5 transition-colors group">
                <div className="flex items-center gap-4 mb-4">
                  <h.icon className="h-6 w-6 text-primary" strokeWidth={1.5} />
                  <h3 className="font-display text-xl font-semibold group-hover:text-primary transition-colors">{h.title}</h3>
                </div>
                <p className="text-[15px] leading-relaxed text-muted-foreground">{h.desc}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* Stats */}
      <section className="mx-auto max-w-7xl px-6 py-24 lg:px-8">
        <Reveal>
          <div className="border-[3px] border-primary/20 bg-primary/5 p-12 sm:p-16">
            <div className="grid gap-12 sm:grid-cols-2 lg:grid-cols-4">
              {stats.map((s, i) => (
                <Reveal key={s.label} delay={i * 0.08}>
                  <div className="text-center">
                    <div className="font-display text-5xl font-semibold tracking-tight text-foreground">{s.value}</div>
                    <div className="mt-4 text-[15px] font-medium text-muted-foreground">{s.label}</div>
                  </div>
                </Reveal>
              ))}
            </div>
          </div>
        </Reveal>
      </section>
    </>
  );
}
