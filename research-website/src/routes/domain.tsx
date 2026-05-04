import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { BookOpen, Lightbulb, Target, ListChecks, Workflow, Layers } from "lucide-react";
import { GlassCard } from "@/components/GlassCard";
import { Reveal } from "@/components/Reveal";

import sdOverall from "../assets/system-diagrams/sd-overall.png";
import sdCae from "../assets/system-diagrams/sd-code-analysis-engine.png";
import sdAcc from "../assets/system-diagrams/sd-ai-code-convertor.png";
import sdDe from "../assets/system-diagrams/sd-decision-engine.png";
import sdHal from "../assets/system-diagrams/sd-hardware-abstraction-layer.png";
import { SectionHeader } from "@/components/SectionHeader";

export const Route = createFileRoute("/domain")({
  head: () => ({
    meta: [
      { title: "Domain - NEXAR Research" },
      { name: "description", content: "Literature survey, research gap, problem, objectives, methodology and technologies behind NEXAR." },
      { property: "og:title", content: "Domain - NEXAR" },
      { property: "og:description", content: "Deep dive into the research foundations of NEXAR." },
    ],
  }),
  component: DomainPage,
});

const sections = [
  { id: "literature", label: "Literature Survey", icon: BookOpen },
  { id: "gap", label: "Research Gap", icon: Lightbulb },
  { id: "problem", label: "Research Problem", icon: Target },
  { id: "objectives", label: "Objectives", icon: ListChecks },
  { id: "methodology", label: "Methodology", icon: Workflow },
  { id: "technologies", label: "Technologies", icon: Layers },
];

const synthesis = "Taken together, the literature reveals a clear pattern. Each of the four sub-problems - multi-language code analysis, ML-driven classical-to-quantum code conversion, intelligent decision-making with economic awareness, and provider-agnostic hardware abstraction - has been addressed in isolation by capable but narrowly-scoped systems. What the field lacks is a single platform that unifies these layers into an automated, cost-aware, feedback-driven pipeline that takes source code as input and produces a routed, executed quantum-or-classical job as output. Nexar (the QCCR platform) is positioned precisely at this intersection, building on the foundations laid by CodeBERT, ScaffCC, Pilot-Quantum, Qiskit Runtime, and prior ML-for-quantum resource-estimation work, while filling the integration gap that none of them individually addresses.";

const literatureItems = [
  {
    title: "Quantum Computing and the NISQ Era",
    content: "Quantum computing exploits quantum-mechanical phenomena - superposition, entanglement, and interference - to process information in ways that classical computers fundamentally cannot. The field today is defined by the Noisy Intermediate-Scale Quantum (NISQ) era, in which quantum processors containing roughly 50 to 1000 qubits are available but remain non-fault-tolerant, with limited coherence times and high gate error rates. These devices can demonstrate quantum advantage for narrowly-defined problem classes such as random circuit sampling, but most general-purpose workloads still run more cheaply and quickly on classical hardware. Major cloud providers - IBM Quantum, Amazon Braket, and Azure Quantum - have made quantum backends publicly accessible, yet the absence of intelligent orchestration tools limits their practical utility for mainstream developers. Consequently, the central research question is no longer whether quantum computing will matter, but for which workloads and under what conditions it offers advantage today."
  },
  {
    title: "Hybrid Quantum-Classical Systems and Resource Management",
    content: "Recognizing that optimal outcomes come from combining paradigms rather than treating them as competitors, researchers have increasingly focused on hybrid quantum-classical systems. Tannu and Qureshi introduced the concept of quantum-aware resource management, showing that naïve scheduling in hybrid environments results in significant resource under-utilization and elevated operational cost. Salavatov and Palacios proposed Pilot-Quantum, a middleware that extends the pilot abstraction model to manage both quantum and classical resources - notably the only existing framework to manage both resource types simultaneously - but it relies on long-running jobs that inflate cost whenever quantum hardware is involved and lacks any predictive or economic optimization capability. Weder et al. proposed automated quantum hardware selection for workflow-based systems, while Lammers et al. articulated the broader set of resource-management challenges specific to the NISQ era. Qiskit Runtime offers session-based quantum execution with classical co-processing, Amazon Braket provides a multi-provider interface without automated workload analysis, and Azure Quantum supplies resource estimation but performs no code-level routing analysis. Across this literature a consistent pattern emerges: existing systems address fragments of the hybrid-computing problem in isolation, without unifying code analysis, decision-making, and execution into a single automated pipeline."
  },
  {
    title: "Static Analysis and Multi-Language Code Analysis",
    content: "Quantum software engineering has begun to develop its own static-analysis toolchain. QChecker was one of the first comprehensive static-analysis frameworks designed for quantum programs, establishing the feasibility of automated quantum bug detection. ScaffCC laid foundational groundwork for scalable quantum-program compilation and analysis, while Q-PAC extended pattern-based analysis by detecting recurring bug-fix patterns in quantum code. The High-Performance Compiler for Quantum Error Correction demonstrated sophisticated circuit-optimization techniques for large-scale error-corrected systems. Abstract Syntax Tree (AST) parsing remains central to this line of work because it abstracts away surface syntax and exposes the semantic structure needed for analysis, and recent work on parsing OpenQASM 3.0 - which introduces timing, pulse control, and gate modifiers - has underscored the complexity of handling multiple quantum dialects simultaneously. Despite these advances, existing tools are language-specific: QChecker, ScaffCC, Q-PAC, and the High-Performance Compiler for QEC each target a single language or narrow framework, and none support unified analysis across Qiskit, Q#, Cirq, and OpenQASM or incorporate machine learning for quantum-algorithm pattern recognition."
  },
  {
    title: "Machine Learning for Code Understanding and Transformation",
    content: "Parallel advances in machine learning for source code have reshaped what is possible in program analysis. Large language models trained on code - CodeT5, CodeBERT, and GPT-based architectures - have demonstrated strong performance on code understanding, classification, and cross-language translation. CodeBERT in particular has been successfully applied to code-classification tasks, and Afrose et al. extended it to translate QASM to QIR, showing that pre-trained code models can meaningfully understand quantum programs. Graph Neural Networks have emerged as complementary tools for reasoning about source-code structure and identifying patterns in computational graphs. Yet the application of these techniques to quantum code generation - automatically converting classical algorithms into functionally-equivalent quantum implementations - remains largely unexplored. Simsek et al. demonstrated that machine learning can effectively optimize quantum circuits, but their work stopped at algorithm-level analysis and did not integrate with real-time system conditions or economic factors. No existing system provides end-to-end automated conversion from classical to quantum code while preserving functional correctness, targeting quantum advantage, and accounting for NISQ noise in its performance predictions."
  },
  {
    title: "Resource Estimation, Cost Modeling, and Performance-per-Cost Analysis",
    content: "A third strand of the literature focuses on estimating the cost and resources required to execute quantum workloads. Beverland et al. developed methods for estimating logical qubit requirements for fault-tolerant algorithms, Quetschlich et al. demonstrated practical resource estimation for quantum application development, and Kashif et al. explored hardware-calibrated quantum cost modeling for resource-aware optimization. However, most of these approaches target future error-corrected devices rather than current NISQ hardware. Current quantum-cloud pricing models are predominantly time-based and give little weight to algorithmic complexity or expected performance gains. Performance-per-cost in quantum computing therefore remains a largely unexplored area: without a principled way to compute the business value of executing a workload on quantum versus classical hardware, it is difficult to provide a defensible routing conclusion. This creates a clear opportunity for systems that combine real-time cloud pricing, algorithmic complexity metrics, and return-on-investment analysis into a unified cost-benefit framework."
  },
  {
    title: "Decision-Making and Workload Routing",
    content: "The decision-making layer that sits above code analysis and cost estimation has itself received scattered attention. Tang et al. proposed AlphaRouter, applying reinforcement learning and tree search to quantum circuit routing. Zhan et al. presented a full-stack framework for high-performance quantum-classical computing. Heddad and Bouanane explored interference-based routing through a hybrid quantum-classical mixture of experts. Chinnaraju proposed a reference architecture for hybrid quantum-classical predictive analytics and decision optimization in business settings. Most existing hybrid orchestration systems, however, rely on static rules and predetermined thresholds, optimize for a single metric such as execution time or accuracy, and lack feedback mechanisms that allow routing quality to improve over time. Very few integrate machine-learning-based suitability prediction with physics-aware rule systems and real-time cost analysis into a single weighted decision framework, and fewer still incorporate post-execution feedback loops that retrain ML models, adjust rule thresholds, and update pricing data based on actual outcomes."
  },
  {
    title: "Provider-Agnostic Execution and Hardware Abstraction",
    content: "Finally, at the execution layer, research on hardware abstraction for hybrid systems has been comparatively sparse. OpenQL demonstrated portable quantum programming across multiple accelerator backends, and serverless paradigms such as the Function-as-a-Service (FaaS) model behind AWS Lambda and Azure Functions have proven successful for cost-efficient short-task execution in classical computing. Extending these principles to quantum workloads - enabling unified API access across IBM Qiskit, AWS Braket, and Azure Quantum with intelligent queue management (fair-share, Shortest Job First, round-robin) - remains an open engineering challenge. Leonidas et al. have shown that qubit-efficient algorithms can make NISQ-era execution more economical, and Salm et al. proposed prioritization of compiled quantum circuits for different quantum computers, but no existing abstraction layer combines provider-agnostic submission, intelligent scheduling, and cost-tracking into a production-ready framework."
  }
];

const overarchingGap = "Despite growing accessibility to quantum hardware through providers like IBM Quantum, AWS Braket, and Azure Quantum, there is no end-to-end system that automatically analyzes source code, decides whether quantum or classical execution is optimal, converts the code if needed, and routes it to the right hardware. Existing research tackles individual pieces of this problem in isolation - a code analyzer here, a middleware scheduler there, an ML cost model elsewhere - but none unify them into a single pipeline that a developer can use without deep quantum expertise. Nexar fills this gap by delivering the first fully automated, cost-aware, multi-language quantum-classical routing platform built for the NISQ era.";

const researchProblemMain = "How can we design an end-to-end, intelligent platform that automatically analyzes source code, decides whether a computational workload is best executed on quantum or classical hardware, converts the code where necessary, and routes it to the optimal backend - while jointly optimizing for execution time, cost, and NISQ-era hardware constraints?";

const researchProblemIntro = "In the current Noisy Intermediate-Scale Quantum (NISQ) era, determining whether a workload benefits from quantum or classical execution is non-trivial. The decision depends on a complex interplay of problem structure, circuit complexity, hardware noise, qubit availability, queue times, transpilation overhead, and real-time cloud pricing. Simply having access to a quantum backend does not guarantee advantage - for many problems, particularly those with polynomial classical solutions, classical execution remains orders of magnitude faster and cheaper. Yet no existing platform gives developers an automated, cost-aware way to make this determination without deep quantum expertise.";

const subProblems = [
  {
    title: "Sub-Problem 1 - Multi-Language Code Analysis",
    question: "How can we build a comprehensive, multi-language code analysis engine that automatically identifies quantum-amenable code patterns, estimates computational complexity, and provides real-time recommendations for optimal quantum-classical workload distribution?",
    desc: "Developers work with heterogeneous codebases spanning Qiskit, Q#, Cirq, and OpenQASM, but existing tools (QChecker, ScaffCC, Q-PAC) analyze only one language or framework at a time. Without unified analysis, automated pattern recognition, and accurate hybrid complexity estimation, developers must manually determine which portions of their applications might benefit from quantum execution - leading to suboptimal resource utilization and blocking integration with interactive development environments."
  },
  {
    title: "Sub-Problem 2 - Automated Classical-to-Quantum Code Conversion",
    question: "How can we develop an intelligent system that automatically converts classical computational code to quantum-equivalent implementations while accurately predicting quantum advantage and maintaining functional correctness?",
    desc: "This problem encompasses five connected challenges: accurately identifying quantum-amenable patterns in classical code, generating syntactically correct and functionally equivalent quantum code, predicting quantum performance advantage while accounting for NISQ device limitations, integrating code conversion into broader hybrid computing workflows, and continuously improving conversion accuracy through feedback learning."
  },
  {
    title: "Sub-Problem 3 - Intelligent, Cost-Aware Decision Making",
    question: "How can we develop a decision-making system that optimally routes computational workloads between quantum and classical resources while considering performance predictions, real-time costs, and system constraints to maximize efficiency and cost-effectiveness in hybrid computing environments?",
    desc: "This sub-problem itself breaks into four challenges:",
    challenges: [
      { name: "Performance prediction", text: "accurately predicting whether a given task will benefit from quantum execution based on code characteristics and algorithmic patterns." },
      { name: "Cost optimization", text: "balancing potential performance gains against the high cost of quantum execution while respecting budget constraints and maximizing return on investment." },
      { name: "Multi-objective decision-making", text: "simultaneously optimizing for execution time, accuracy, cost, and resource availability while handling conflicting objectives and trade-offs." },
      { name: "Real-time adaptation", text: "continuously learning from execution outcomes and adapting decision models to changing conditions, hardware capabilities, and workload characteristics." }
    ]
  },
  {
    title: "Sub-Problem 4 - Provider-Agnostic, Cost-Effective Execution",
    question: "How can we build a hardware abstraction layer that unifies heterogeneous quantum and classical resources behind a single API, routes workloads cost-effectively across multiple providers, and scales efficiently for short-lived hybrid jobs?",
    desc: "Quantum-friendly operations represent only a fraction of real-world computing workloads, and cost-effective solutions to automatically route workloads to matching hardware do not yet exist due to limited research in this area. Existing middleware such as Pilot-Quantum manages both resource types but relies on long-running jobs that inflate cost on quantum hardware. Performance-per-cost in quantum computing remains a largely unexplored area, and without a solid way to calculate the business value of executing a task on quantum versus classical hardware, organizations cannot confidently commit to hybrid infrastructure."
  }
];

const researchSignificance = "This problem is particularly urgent as quantum cloud services from IBM, AWS, and Microsoft become more accessible and organizations seek to integrate quantum capabilities into existing software workflows. The absence of an automated, cost-aware routing platform represents a significant barrier to the practical adoption of hybrid quantum-classical computing. By solving all four sub-problems in a single integrated pipeline, Nexar aims to serve as both a practical decision-support tool for the NISQ era and a readiness-ready infrastructure for the fault-tolerant quantum computing era to come.";

const specificObjectives = [
  {
    title: "SO1 - Code Analysis Engine (CAE)",
    desc: "Design and develop a comprehensive, multi-language Code Analysis Engine that automatically inspects, characterizes, and classifies source code segments across heterogeneous quantum programming languages to drive downstream routing decisions.",
    points: [
      "Design a unified multi-language parsing and analysis framework with AST-based parsers for Python/Qiskit, Q#, Cirq, and OpenQASM, normalized through a language-agnostic intermediate representation (IR).",
      "Develop quantum operation detection algorithms that recognize gates (H, CNOT, T), measurements, qubit allocation/deallocation, and circuit topologies, translating language-specific intrinsics into a standardized operation set.",
      "Implement comprehensive complexity analysis modules covering cyclomatic complexity, classical time/space complexity (Big-O), quantum resource estimates (qubit count, gate depth, circuit width), and parallelization potential.",
      "Integrate machine-learning-based pattern recognition to detect canonical quantum algorithms (Grover's, Shor's, QFT, QAOA, VQE) and classify code suitability for quantum execution.",
      "Enable low-latency analysis suitable for interactive development environments and real-time routing pipelines."
    ]
  },
  {
    title: "SO2 - Decision Engine (DE)",
    desc: "Develop an intelligent Decision Engine that optimally routes workloads between quantum and classical resources using machine-learning-based performance prediction, rule-based validation, and real-time cost-benefit analysis.",
    points: [
      "Core decision model development - train ML models (Random Forest, XGBoost, Neural Networks in an ensemble) capable of predicting optimal hardware allocation from code analysis features, achieving a minimum of 85% accuracy on benchmark problems.",
      "Rule-based validation system - implement threshold-based rules and compatibility checks that enforce safety constraints and handle clear-cut routing cases deterministically across supported quantum and classical backends.",
      "Cost analysis framework - build a component that consumes live provider pricing, estimates execution time, computes ROI, and enables cost-aware routing within budget categories.",
      "System integration and testing - unify ML, rules, and cost analysis through weighted voting and a Decision Merger with confidence scoring and conflict resolution, then validate improvement over baseline rule-based routing.",
      "Evaluation and future-work identification - conduct systematic evaluation, document performance, and specify extensions for advanced adaptive learning and real-time optimization."
    ]
  },
  {
    title: "SO3 - AI Code Converter (ACC)",
    desc: "Develop an AI-powered code converter that automatically transforms selected classical Python algorithms into Qiskit quantum implementations while predicting quantum advantage for NISQ devices.",
    points: [
      "Large Language Model implementation - fine-tune the CodeT5-base model on 200-500 curated classical-to-quantum algorithm pairs targeting 5-10 well-defined patterns, achieving 90% conversion accuracy.",
      "Pattern recognition system development - build an AST-based recognition engine backed by a pattern database of 50 algorithmic signatures, reaching 85% accuracy on target pattern detection within classical Python code.",
      "Performance prediction module - use Qiskit Aer simulators with basic noise models to estimate runtime, speedup, and NISQ-viability, targeting 80% accuracy in predicting realistic quantum advantage.",
      "System integration and validation - expose the pipeline through a REST API and web interface, validate on 10 benchmark algorithms against known manual quantum implementations, and implement feedback-based learning using execution results."
    ]
  },
  {
    title: "SO4 - Hardware Abstraction Layer (HAL)",
    desc: "Build a hardware abstraction layer that unifies heterogeneous quantum and classical resources behind a single API and manages their cost-effective, short-term utilization.",
    points: [
      "Develop a standardized set of APIs - design a unified API layer that abstracts differences between quantum and classical hardware, exposes job submission/monitoring/result retrieval, and supports extensibility for new backends (QPUs, classical clusters, GPUs, cloud instances) without changing upper layers.",
      "Implement a decision engine for resource routing - automatically select the most suitable hardware based on workload characteristics, user-defined constraints, and performance requirements, supporting cost-optimization, performance-optimization, and availability-based routing policies, plus manual override.",
      "Develop a resource management framework - create a scheduler supporting fair-share, Shortest Job First (SJF), and round-robin policies; ensure fault tolerance and automatic failover; implement load balancing; and track usage across quantum and classical backends.",
      "Enable real-time resource monitoring - continuously monitor availability and queue lengths across IBM Quantum, AWS Braket, Azure Quantum, and classical compute, feeding status updates back to the Decision Engine."
    ]
  }
];

const expectedOutcomes = [
  "Multi-language code analysis covering Python, Qiskit, Q#, Cirq, and OpenQASM, with >85% pattern-recognition accuracy.",
  "Automated classical-to-quantum conversion with 85%+ conversion accuracy and 90%+ quantum-advantage prediction accuracy on selected algorithm categories.",
  "Intelligent, cost-aware routing decisions with 85%+ hardware recommendation accuracy, decision latency under 2 minutes, and a feedback loop that continuously retrains the ML model, adjusts rule thresholds, and updates cost models.",
  "Provider-agnostic execution across IBM Qiskit, AWS Braket, and Azure Quantum with unified APIs, intelligent scheduling, and FaaS-style short-task execution.",
  "An empirical cost-benefit evaluation across 100 diverse workloads (classical, hybrid, and pure quantum), characterizing the quantum-classical crossover point and demonstrating the platform's practical utility as a decision-support tool for the NISQ era and a readiness-ready infrastructure for the fault-tolerant era to come."
];

const componentGaps = [
  {
    title: "Code Analysis Engine",
    subtitle: "No unified, multi-language, ML-enhanced quantum code analyzer",
    desc: "Existing tools like QChecker (2023), ScaffCC (2014), Q-PAC (2023), and the High-Performance Compiler for QEC (2022) each handle only narrow slices of quantum code analysis, and none combine machine-learning-based pattern recognition with support for multiple quantum languages (Qiskit, Q#, Cirq, OpenQASM). Developers working with heterogeneous codebases have no single tool that can simultaneously detect quantum-amenable segments, estimate complexity, and adapt to evolving hardware characteristics with low enough latency for real-time use.",
  },
  {
    title: "Decision Engine",
    subtitle: "No integrated, adaptive, economically aware routing intelligence",
    desc: "Current hybrid systems rely on static rules and predetermined thresholds, optimize for single metrics (time or accuracy, not both), and treat technical performance separately from cost. Prior work such as Tannu & Qureshi's quantum-aware resource management and Salavatov & Palacios's Pilot-Quantum middleware lacks predictive ML, feedback-driven learning, real-time cost analysis with live provider pricing, and multi-objective optimization across cost, performance, and reliability.",
  },
  {
    title: "AI Code Converter",
    subtitle: "No automated classical-to-quantum translation pipeline",
    desc: "No existing system offers end-to-end automated conversion from classical code into quantum equivalents while preserving functional correctness, targeting quantum advantage, and providing noise-aware performance prediction for NISQ devices. Existing quantum simulators assume ideal conditions, current pattern-recognition tools cannot reliably identify quantum-suitable algorithmic structures, and no tool integrates conversion with feedback-driven optimization based on real execution outcomes.",
  },
  {
    title: "Hardware Abstraction Layer",
    subtitle: "No provider-agnostic, cost-optimized execution layer",
    desc: "Performance-per-cost in quantum computing is a largely unexplored area. Pilot-Quantum is currently the only middleware that manages both quantum and classical resources, but it relies on long-running jobs that inflate cost on quantum hardware. Existing frameworks also lack a unified API spanning IBM Qiskit, AWS Braket, and Azure Quantum with intelligent queue management (fair-share, SJF, round-robin) that would let a single workload transparently target the most suitable backend.",
  }
];

const novelties = [
  {
    component: "Code Analysis Engine",
    gap: "Fragmented, single-language static analysis",
    contribution: "Multi-language AST parsing + CodeBERT-based ML classification in a unified framework"
  },
  {
    component: "AI Code Converter",
    gap: "Manual classical-to-quantum translation",
    contribution: "Fine-tuned CodeT5 + noise-aware performance prediction for NISQ devices"
  },
  {
    component: "Decision Engine",
    gap: "Static, single-metric, cost-blind routing",
    contribution: "Hybrid ML ensemble (50%) + physics-aware rules (35%) + real-time cost analyzer (15%) with feedback-driven retraining"
  },
  {
    component: "Hardware Abstraction Layer",
    gap: "Provider lock-in, cost-unaware scheduling",
    contribution: "Unified API across IBM/AWS/Azure with fair-share/SJF/round-robin scheduling and FaaS-style short-task execution"
  }
];

const methodologyArchitectureIntro = "Nexar is implemented as a microservices monorepo comprising six independently-deployable services that communicate through a central Express.js API Gateway (JWT-authenticated). The architecture is designed for modularity so that each component can scale independently and be updated without disrupting the others. All services are containerized with Docker and deployed on Google Cloud Platform via Cloud Run, with infrastructure managed through Terraform.";

const methodologyPipeline = [
  "The user submits source code through a web interface or REST API.",
  "The Code Analysis Engine (CAE) detects the language, computes complexity metrics, and classifies the algorithm.",
  "If the submitted code is classical but could benefit from quantum execution, the AI Code Converter (ACC) translates it into a Qiskit quantum circuit.",
  "The Decision Engine (DE) consumes the analysis features and - through a weighted combination of ML prediction, physics-aware rules, and real-time cost analysis - produces a hardware recommendation with a confidence score.",
  "The Hardware Abstraction Layer (HAL) submits the job to the selected backend (IBM Qiskit, AWS Braket, Azure Quantum, or a classical runtime) through a unified provider-agnostic interface.",
  "Execution results are returned to the user, and post-execution data is fed back into the Decision Engine to retrain models, adjust thresholds, and refine cost estimates."
];

const componentMethodologies = [
  {
    title: "1. Code Analysis Engine (CAE)",
    desc: "The CAE is the analytical foundation of the pipeline, transforming raw source code into a structured feature set consumed by downstream components.",
    img: sdCae,
    points: [
      "Language detection - an ML-based classifier identifies one of five frameworks (Python, Qiskit, Cirq, Q#, OpenQASM) with confidence scores above 0.85.",
      "Metrics extraction - tree-sitter-based AST parsing computes cyclomatic complexity, cognitive complexity, time/space complexity classification (O(1) through O(2ⁿ)), loop count, and nesting depth.",
      "Algorithm classification - a three-tier approach combining CodeBERT transformer-based semantic understanding, ensemble machine learning, and rule-based pattern matching detects canonical quantum algorithms such as Grover's, Shor's, QFT, QAOA, and VQE.",
      "Feature vector construction - a 16-dimensional feature vector capturing circuit complexity, entanglement properties, and NISQ-viability metrics is forwarded to the Decision Engine without requiring manual annotation."
    ]
  },
  {
    title: "2. AI Code Converter (ACC)",
    desc: "The ACC intelligently translates classical Python algorithms into Qiskit quantum implementations for selected algorithm categories. The methodology unfolds in four phases:",
    img: sdAcc,
    points: [
      "Phase 1 Foundation (Months 1-3) - Literature review of classical-to-quantum conversion approaches, curation of 200-500 classical-quantum algorithm pairs, environment setup, and CodeT5-base integration.",
      "Phase 2 Component Development (Months 4-6) - AST-based pattern recognition with a basic GNN, pattern database of 50 algorithmic signatures, fine-tuning CodeT5, and integrating Qiskit Aer for performance prediction.",
      "Phase 3 Integration and Optimization (Months 7-8) - Unification of LLM, pattern recognition, and performance-prediction through a REST API; benchmark testing; web dashboard development.",
      "Phase 4 Validation and Deployment (Months 9-10) - Final validation against community-reviewed code, measurement of accuracy metrics, followed by documentation."
    ]
  },
  {
    title: "3. Decision Engine (DE)",
    desc: "The Decision Engine operates as a multi-layered routing system with five processing layers: Feature Extractor → ML Model → Rule System → Cost Analyzer → Decision Merger.",
    img: sdDe,
    points: [
      "Initiation and Planning (Months 1-2) - Requirements specification, technology selection, and baseline architecture design.",
      "Foundation and Input Processing (Months 2-3) - Feature extraction, complexity-metric normalization, pattern extraction, and a Validation Processor for constraints and compatibility.",
      "ML Deployment (Months 3-5) - Ensemble models trained on benchmark data, parallel rule system for threshold rules, and a cost analyzer for static costs, execution-time, and ROI.",
      "Integration and Testing (Months 6-7) - The Decision Merger combines ML (50% weight), rule (35%), and cost (15%) outputs through weighted voting and conflict resolution.",
      "Output and Feedback (Month 7+) - Returns a primary hardware choice plus alternatives. A feedback processor collects execution results to retrain ML and adjust rules."
    ]
  },
  {
    title: "4. Hardware Abstraction Layer (HAL)",
    desc: "The HAL exposes a unified API across heterogeneous backends and manages their efficient utilization.",
    img: sdHal,
    points: [
      "Unified API design - abstracts differences between quantum (IBM Quantum, IonQ, Google Quantum AI) and classical (local clusters, AWS EC2, GCP) backends, exposing common data formats.",
      "Resource management and scheduling - a scheduler supporting fair-share, SJF, and round-robin handles queue management across separate quantum/classical queues. Fault tolerance and failover enforced here.",
      "Short-term task execution - inspired by FaaS models (AWS Lambda), optimizing for short, bursty workloads rather than long-running jobs to remain cost-effective.",
      "Real-time monitoring - continuous tracking of availability and queue lengths across all resources, feeding status updates back to the Decision Engine every 30 seconds."
    ]
  }
];

const methodologyData = [
  { name: "Training data", text: "synthetic computational problems across different complexity classes, canonical benchmark algorithms (QAOA, VQE, Shor's, Grover's), historical execution data, and real-time cost/performance data from quantum cloud providers." },
  { name: "Storage architecture", text: "separate stores for cost models (pricing history, budget tracking, cost predictions), performance metrics (accuracy, response times, prediction success rates), and execution history (past decisions, outcomes, lessons learned)." },
  { name: "Evaluation datasets", text: "standard quantum computing benchmarks, classical optimization problems, mixed hybrid scenarios, and edge-case workloads for robustness testing." }
];

const validationStrategy = {
  intro: "Validation is conducted across 100 diverse workloads in three categories:",
  categories: [
    { name: "Classical (32)", desc: "deep learning (CNN, transformer, GAN), scientific computing (molecular dynamics, CFD, N-body, PDE), ML (k-means, gradient boosting, reinforcement learning), cryptography (RSA, AES), and combinatorial optimization (TSP, graph coloring, A*)." },
    { name: "Hybrid (23)", desc: "VQE variants, QAOA (supply chain, graph partitioning), quantum ML (QSVM, QNN, quantum transfer learning), and quantum error mitigation (ZNE) with qubit counts of 0-24." },
    { name: "Quantum (45)", desc: "molecular simulation (H₂, LiH, H₂O, iron-sulfur protein, 120-qubit VQE), factoring (Shor's), search (Grover's, 3-SAT), optimization (QAOA MaxCut, vehicle routing), and foundational algorithms (Deutsch-Jozsa, Bernstein-Vazirani, Simon's, QFT, QPE) with qubit counts of 1-150." }
  ],
  conclusion: "Metrics collected include routing accuracy, pipeline latency, decision inference time, conversion accuracy, pattern-recognition accuracy, quantum-advantage prediction accuracy, and the quantum-classical cost crossover point. Non-functional requirements set hard targets of <2 s routing latency, <500 ms API response time, 99.5% uptime, support for 100+ concurrent jobs, and resource status updates every 30 s."
};

const technologyCategories = [
  {
    title: "Programming Languages",
    items: [
      { name: "Python 3.9+", desc: "Core language for all ML models, quantum circuit construction, code analysis, and backend services" },
      { name: "Node.js / TypeScript", desc: "API Gateway and inter-service communication layer" },
      { name: "JavaScript / TypeScript", desc: "Frontend web interface" }
    ]
  },
  {
    title: "Machine Learning & AI",
    items: [
      { name: "TensorFlow 2.x", desc: "Neural network models for performance prediction and pattern recognition" },
      { name: "PyTorch", desc: "Alternative deep learning framework for select model experiments" },
      { name: "Scikit-learn", desc: "Classical ML algorithms and preprocessing pipelines" },
      { name: "XGBoost", desc: "Gradient boosting models in the Decision Engine ensemble" },
      { name: "CodeBERT", desc: "Pre-trained transformer for code classification across five quantum frameworks" },
      { name: "CodeT5-base", desc: "Fine-tuned model for classical-to-quantum code conversion" },
      { name: "Graph Neural Networks (GNN)", desc: "Structural pattern detection in AST graphs" }
    ]
  },
  {
    title: "Quantum Computing Frameworks",
    items: [
      { name: "Qiskit", desc: "IBM's quantum SDK — primary framework for circuit construction and Aer simulation" },
      { name: "Qiskit Aer", desc: "Noise-aware quantum simulation for performance prediction" },
      { name: "Cirq", desc: "Google's quantum library for Cirq-based workloads" },
      { name: "Q# (Microsoft QDK)", desc: "Microsoft quantum development kit support" },
      { name: "OpenQASM 3.0", desc: "Quantum assembly language with timing, pulse control, and gate modifiers" },
      { name: "Forest SDK", desc: "Rigetti quantum computing support" }
    ]
  },
  {
    title: "Quantum Cloud Providers",
    items: [
      { name: "IBM Quantum", desc: "Primary quantum backend — 127-qubit Eagle processors and simulators" },
      { name: "AWS Braket", desc: "Multi-vendor quantum hardware access" },
      { name: "Azure Quantum", desc: "Microsoft's quantum computing service" }
    ]
  },
  {
    title: "Code Parsing & Analysis",
    items: [
      { name: "ANTLR4", desc: "Multi-language parser generator for Qiskit, Q#, Cirq, and OpenQASM" },
      { name: "tree-sitter", desc: "AST-based parsing for classical software metrics extraction" },
      { name: "Python ast module", desc: "Lightweight AST extraction in the AI Code Converter" }
    ]
  },
  {
    title: "Web Frameworks & APIs",
    items: [
      { name: "FastAPI", desc: "RESTful API implementation for Python-based microservices" },
      { name: "Express.js", desc: "JWT-authenticated API Gateway" },
      { name: "RESTful APIs", desc: "Unified communication across all microservices" }
    ]
  },
  {
    title: "Data Storage",
    items: [
      { name: "PostgreSQL", desc: "Execution history, decision logs, cost models, and persistent data" },
      { name: "Redis", desc: "Real-time data caching for hardware status and pricing feeds" }
    ]
  },
  {
    title: "DevOps & Deployment",
    items: [
      { name: "Docker", desc: "Containerization of all microservices" },
      { name: "Google Cloud Run", desc: "Serverless container deployment platform" },
      { name: "Google Cloud Platform (GCP)", desc: "Primary cloud infrastructure" },
      { name: "Terraform", desc: "Infrastructure as Code for reproducible deployments" },
      { name: "Git (GitHub/GitLab)", desc: "Version control with CI/CD pipelines" },
      { name: "Kubernetes", desc: "Container orchestration support for scaling" }
    ]
  },
  {
    title: "Testing & Quality",
    items: [
      { name: "Unit testing frameworks", desc: "Component validation with 80%+ code coverage" },
      { name: "Integration testing", desc: "End-to-end workflow validation including feedback loops" },
      { name: "Performance testing", desc: "Scalability testing under load" },
      { name: "Benchmark suite", desc: "100 classical, hybrid, and quantum algorithms for validation" }
    ]
  }
];

const technologiesArchitectureSummary = `User → React Frontend
      ↓
Express.js API Gateway (JWT)
      ↓
Code Analysis Engine (FastAPI + tree-sitter + CodeBERT)
      ↓
AI Code Converter (CodeT5 + Qiskit Aer)
      ↓
Decision Engine (XGBoost + Random Forest + Neural Networks)
      ↓
Hardware Abstraction Layer (Qiskit / Braket / Azure SDKs)
      ↓
IBM Quantum / AWS Braket / Azure Quantum / Classical Runtime
      ↓
PostgreSQL (persistent) + Redis (cache)

All containerized with Docker · Deployed on GCP Cloud Run · Managed via Terraform`;

function DomainPage() {
  const [activeSection, setActiveSection] = useState<string>("");

  useEffect(() => {
    const handleScroll = () => {
      const sectionElements = document.querySelectorAll("section[id]");
      let current = "";
      
      sectionElements.forEach((section) => {
        const sectionTop = section.getBoundingClientRect().top;
        if (sectionTop <= 250) {
          current = section.id;
        }
      });
      
      if (current) {
        setActiveSection(current);
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    // setTimeout ensures elements are painted before initial check
    setTimeout(handleScroll, 100);

    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <>
      <section className="border-b border-border">
        <div className="mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:px-8">
          <SectionHeader
            eyebrow="Research Domain"
            title="The science behind NEXAR."
            subtitle="From foundational literature to applied methodology - explore every layer of the project."
          />
        </div>
      </section>

      <div className="mx-auto grid max-w-7xl gap-16 px-6 py-20 lg:grid-cols-[220px_1fr] lg:px-8">
        <aside className="lg:sticky lg:top-24 lg:self-start">
          <nav>
            <p className="mb-4 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Sections</p>
            <ul className="space-y-1">
              {sections.map((s) => (
                <li key={s.id}>
                  <a
                    href={`#${s.id}`}
                    className={`flex items-center gap-2.5 rounded-md px-2 py-1.5 text-sm transition-all duration-200 ${
                      activeSection === s.id
                        ? "bg-primary/10 text-primary font-medium"
                        : "text-muted-foreground hover:bg-muted hover:text-foreground"
                    }`}
                  >
                    <s.icon className="h-3.5 w-3.5 transition-all" strokeWidth={activeSection === s.id ? 2.2 : 1.8} />
                    {s.label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>
        </aside>

        <div className="space-y-20">
          <Section id="literature" icon={BookOpen} title="Literature Survey">
            <div className="space-y-16">
              <div className="divide-y divide-border border-y border-border">
                {literatureItems.map((item, i) => (
                  <Reveal key={item.title} delay={i * 0.05}>
                    <div className="group flex flex-col gap-3 py-8 sm:flex-row sm:gap-8 md:gap-12 md:py-12">
                      <div className="shrink-0 pt-0.5 sm:w-20">
                        <span className="font-display text-5xl font-light tracking-tighter text-muted-foreground/20 transition-colors duration-500 group-hover:text-primary">
                          0{i + 1}
                        </span>
                      </div>
                      <div className="flex-1">
                        <h4 className="font-display text-xl font-semibold tracking-tight text-foreground sm:text-2xl mb-4">
                          {item.title}
                        </h4>
                        <p className="text-[15px] leading-relaxed text-muted-foreground max-w-4xl">
                          {item.content}
                        </p>
                      </div>
                    </div>
                  </Reveal>
                ))}
              </div>
              
              <Reveal delay={0.2}>
                <div className="group flex flex-col gap-3 py-8 sm:flex-row sm:gap-8 md:gap-12 md:py-12 border-b border-border bg-primary/5 -mx-6 px-6 sm:-mx-8 sm:px-8 rounded-b-3xl">
                  <div className="shrink-0 flex items-center pt-0.5 sm:w-20">
                    <div className="h-1 w-8 bg-primary/40 rounded-full transition-all duration-500 group-hover:w-12 group-hover:bg-primary" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-display text-xl font-semibold tracking-tight text-foreground sm:text-2xl mb-4">
                      Synthesis
                    </h4>
                    <p className="text-[15px] leading-relaxed text-foreground/80 max-w-4xl">
                      {synthesis}
                    </p>
                  </div>
                </div>
              </Reveal>
            </div>
          </Section>

          <Section id="gap" icon={Lightbulb} title="Research Gap">
            <div className="space-y-12">
              <div className="prose-muted">
                <p className="leading-relaxed">{overarchingGap}</p>
              </div>
              
              <div className="space-y-6">
                <h4 className="font-display text-xl font-semibold text-foreground">Component-Level Gaps Addressed by Nexar</h4>
                <div className="mt-8 divide-y divide-border border-y border-border">
                  {componentGaps.map((gap, i) => (
                    <Reveal key={gap.title} delay={i * 0.05}>
                      <div className="group flex flex-col gap-3 py-8 sm:flex-row sm:gap-8 md:gap-12">
                        <div className="shrink-0 pt-0.5 sm:w-20">
                          <span className="font-display text-5xl font-light tracking-tighter text-muted-foreground/20 transition-colors duration-500 group-hover:text-primary">
                            0{i + 1}
                          </span>
                        </div>
                        <div className="flex-1">
                          <h5 className="font-display text-xl font-semibold tracking-tight text-foreground sm:text-2xl mb-2">
                            {gap.title}
                          </h5>
                          <div className="mb-4 text-[13px] font-medium text-primary tracking-wide uppercase">
                            {gap.subtitle}
                          </div>
                          <p className="text-[15px] leading-relaxed text-muted-foreground max-w-3xl">
                            {gap.desc}
                          </p>
                        </div>
                      </div>
                    </Reveal>
                  ))}
                </div>
              </div>

              <div className="space-y-6">
                <div>
                  <h4 className="font-display text-xl font-semibold text-foreground">What Makes Nexar's Approach Novel</h4>
                  <p className="text-sm mt-1 text-muted-foreground">Nexar closes these gaps simultaneously by integrating four components into one pipeline:</p>
                </div>
                <div className="overflow-hidden rounded-xl border border-border bg-surface/50 backdrop-blur-sm">
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead>
                        <tr className="border-b border-border bg-muted/50">
                          <th className="px-5 py-4 font-semibold text-foreground">Component</th>
                          <th className="px-5 py-4 font-semibold text-foreground">Gap It Closes</th>
                          <th className="px-5 py-4 font-semibold text-foreground">Novel Contribution</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border">
                        {novelties.map((novelty) => (
                          <tr key={novelty.component} className="transition-colors hover:bg-muted/30">
                            <td className="px-5 py-4 font-medium text-foreground whitespace-nowrap">{novelty.component}</td>
                            <td className="px-5 py-4 text-muted-foreground leading-relaxed">{novelty.gap}</td>
                            <td className="px-5 py-4 text-foreground leading-relaxed">{novelty.contribution}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </Section>

          <Section id="problem" icon={Target} title="Research Problem">
            <div className="space-y-16">
              <div className="space-y-6">
                <blockquote className="border-l-[3px] border-primary bg-primary/5 p-6 sm:p-8 rounded-r-2xl">
                  <p className="font-display text-xl leading-relaxed text-foreground sm:text-2xl font-medium">
                    "{researchProblemMain}"
                  </p>
                </blockquote>
                <p className="text-[16px] leading-relaxed text-muted-foreground w-full">
                  {researchProblemIntro}
                </p>
              </div>

              <div className="space-y-10">
                <h4 className="font-display text-2xl font-semibold text-foreground border-b border-border pb-4">
                  Problem Decomposition
                </h4>
                
                <div className="grid gap-12 sm:grid-cols-2">
                  {subProblems.map((sp, i) => (
                    <Reveal key={sp.title} delay={i * 0.05}>
                      <div className="flex flex-col border-t-[3px] border-primary/20 pt-6 transition-colors hover:border-primary">
                        <h4 className="font-display text-xs font-bold tracking-[0.2em] text-primary uppercase mb-3">
                          Sub-Problem 0{i + 1}
                        </h4>
                        <h5 className="font-display text-xl font-semibold text-foreground leading-tight mb-5">
                          {sp.title.split(' - ')[1]}
                        </h5>
                        <div className="mb-5 rounded-xl border border-primary/20 bg-primary/5 p-5 text-[15px] font-medium leading-relaxed text-primary/90">
                          {sp.question}
                        </div>
                        <p className="text-[15px] leading-relaxed text-muted-foreground">
                          {sp.desc}
                        </p>
                        {sp.challenges && (
                          <ul className="mt-5 space-y-3">
                            {sp.challenges.map((c) => (
                              <li key={c.name} className="flex items-start gap-3 text-[14px] leading-relaxed">
                                <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/40 border border-primary/20" />
                                <span className="text-muted-foreground">
                                  <strong className="font-semibold text-foreground/80">{c.name}</strong> - {c.text}
                                </span>
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    </Reveal>
                  ))}
                </div>
              </div>

              <Reveal delay={0.2}>
                <div className="group flex flex-col gap-3 py-8 sm:flex-row sm:gap-8 md:gap-12 md:py-12 border-y border-border">
                  <div className="shrink-0 flex items-center pt-0.5 sm:w-20">
                    <div className="h-1 w-8 bg-primary/40 rounded-full transition-all duration-500 group-hover:w-12 group-hover:bg-primary" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-display text-xl font-semibold tracking-tight text-foreground sm:text-2xl mb-4">
                      Significance
                    </h4>
                    <p className="text-[15px] leading-relaxed text-muted-foreground max-w-4xl">
                      {researchSignificance}
                    </p>
                  </div>
                </div>
              </Reveal>
            </div>
          </Section>

          <Section id="objectives" icon={ListChecks} title="Research Objectives">
            <div className="space-y-16">
              <div className="space-y-6">
                <h4 className="font-display text-2xl font-semibold text-foreground border-b border-border pb-4">
                  Main Objective
                </h4>
                <p className="text-[16px] leading-relaxed text-muted-foreground w-full">
                  To design and develop <strong className="text-foreground">Nexar</strong> - an end-to-end, intelligent Quantum-Classical Code Router (QCCR) platform that automatically analyzes source code, decides whether each workload should run on quantum or classical hardware, converts the code where beneficial, and routes it to the optimal backend across multiple cloud providers - while jointly optimizing for execution time, monetary cost, and NISQ-era hardware constraints.
                </p>
                <p className="text-[16px] leading-relaxed text-muted-foreground w-full">
                  The platform is envisioned as a serverless backend analogous to AWS Lambda or Google Cloud Run, but uniquely capable of managing, utilizing, and optimizing quantum hardware for short-term executions in a cost-effective manner.
                </p>
              </div>

              <div className="space-y-10">
                <h4 className="font-display text-2xl font-semibold text-foreground border-b border-border pb-4">
                  Specific Objectives
                </h4>
                
                <div className="space-y-12">
                  {specificObjectives.map((so, i) => (
                    <Reveal key={so.title} delay={i * 0.05}>
                      <div className="flex flex-col gap-6 md:flex-row md:gap-12 group">
                        <div className="md:w-1/3 shrink-0">
                          <h4 className="font-display text-xs font-bold tracking-[0.2em] text-primary uppercase mb-3">
                            Objective 0{i + 1}
                          </h4>
                          <h5 className="font-display text-xl font-semibold text-foreground leading-tight mb-4 group-hover:text-primary transition-colors">
                            {so.title.split(' - ')[1]}
                          </h5>
                          <p className="text-[14px] leading-relaxed text-muted-foreground">
                            {so.desc}
                          </p>
                        </div>
                        <div className="md:w-2/3 border-l-2 border-border pl-6 md:pl-8">
                          <ul className="space-y-4">
                            {so.points.map((pt, j) => {
                              const parts = pt.split(' - ');
                              return (
                                <li key={j} className="text-[14.5px] leading-relaxed text-muted-foreground flex gap-3">
                                  <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/40 border border-primary/20" />
                                  <span>
                                    {parts.length > 1 ? (
                                      <>
                                        <strong className="font-medium text-foreground">{parts[0]}</strong> - {parts.slice(1).join(' - ')}
                                      </>
                                    ) : (
                                      pt
                                    )}
                                  </span>
                                </li>
                              )
                            })}
                          </ul>
                        </div>
                      </div>
                    </Reveal>
                  ))}
                </div>
              </div>

              <div className="space-y-8">
                <h4 className="font-display text-2xl font-semibold text-foreground border-b border-border pb-4">
                  Expected Outcomes
                </h4>
                <ul className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3 pt-2">
                  {expectedOutcomes.map((outcome, i) => (
                    <Reveal key={i} delay={i * 0.05}>
                      <li className="flex flex-col gap-4 group">
                        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary font-display font-semibold group-hover:bg-primary group-hover:text-primary-foreground transition-all duration-300 ring-4 ring-primary/5">
                          {i + 1}
                        </div>
                        <p className="text-[14.5px] leading-relaxed text-muted-foreground">
                          {outcome}
                        </p>
                      </li>
                    </Reveal>
                  ))}
                </ul>
              </div>
            </div>
          </Section>

          <Section id="methodology" icon={Workflow} title="Methodology">
            <div className="space-y-16">
              <div className="space-y-6">
                <h4 className="font-display text-2xl font-semibold text-foreground border-b border-border pb-4">
                  Overall System Architecture
                </h4>
                <p className="text-[16px] leading-relaxed text-muted-foreground w-full">
                  {methodologyArchitectureIntro}
                </p>

                <div className="mt-8 py-4 sm:py-8 relative z-0 flex justify-center">
                  <img src={sdOverall} alt="Overall System Architecture" className="w-full max-w-4xl object-contain mix-blend-multiply dark:mix-blend-normal" />
                </div>
                
                <div className="mt-8 rounded-xl border border-primary/20 bg-primary/5 p-6 sm:p-8">
                  <h5 className="font-display text-lg font-semibold text-foreground mb-4">Pipeline Architecture</h5>
                  <ul className="space-y-4">
                    {methodologyPipeline.map((step, i) => (
                      <li key={i} className="flex items-start gap-4 text-[14.5px] leading-relaxed text-muted-foreground">
                        <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-background border border-primary/30 text-primary font-bold text-xs mt-0.5">
                          {i + 1}
                        </div>
                        <span className="flex-1">{step}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="space-y-10">
                <h4 className="font-display text-2xl font-semibold text-foreground border-b border-border pb-4">
                  Component Methodologies
                </h4>
                <div className="space-y-12">
                  {componentMethodologies.map((cm, i) => (
                    <Reveal key={cm.title} delay={i * 0.05}>
                      <div className="flex flex-col border-t-[3px] border-primary/20 pt-6 transition-colors hover:border-primary group">
                        <h5 className="font-display text-xl font-semibold text-foreground leading-tight mb-4 group-hover:text-primary transition-colors">
                          {cm.title}
                        </h5>
                        <p className="text-[15px] leading-relaxed text-muted-foreground mb-6">
                          {cm.desc}
                        </p>
                        <div className="mb-8 py-4 sm:py-6 relative z-0 flex justify-center">
                          <img src={cm.img} alt={cm.title} className="w-full max-w-3xl object-contain mix-blend-multiply dark:mix-blend-normal" />
                        </div>
                        <ul className="grid gap-x-8 gap-y-4 sm:grid-cols-2">
                          {cm.points.map((pt, j) => {
                            const parts = pt.split(' - ');
                            return (
                              <li key={j} className="text-[14px] leading-relaxed text-muted-foreground flex gap-3">
                                <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/40 border border-primary/20" />
                                <span>
                                  {parts.length > 1 ? (
                                    <>
                                      <strong className="font-medium text-foreground">{parts[0]}</strong> - {parts.slice(1).join(' - ')}
                                    </>
                                  ) : (
                                    pt
                                  )}
                                </span>
                              </li>
                            )
                          })}
                        </ul>
                      </div>
                    </Reveal>
                  ))}
                </div>
              </div>

              <div className="grid gap-12 lg:grid-cols-2">
                <div className="space-y-8">
                  <h4 className="font-display text-2xl font-semibold text-foreground border-b border-border pb-4">
                    Data Requirements
                  </h4>
                  <ul className="space-y-4">
                    {methodologyData.map((d, i) => (
                      <Reveal key={i} delay={i * 0.05}>
                        <li className="flex gap-4">
                          <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/40 border border-primary/20" />
                          <p className="text-[14.5px] leading-relaxed text-muted-foreground">
                            <strong className="font-medium text-foreground">{d.name}</strong> - {d.text}
                          </p>
                        </li>
                      </Reveal>
                    ))}
                  </ul>
                </div>

                <div className="space-y-8">
                  <h4 className="font-display text-2xl font-semibold text-foreground border-b border-border pb-4">
                    Testing & Validation Strategy
                  </h4>
                  <p className="text-[14.5px] leading-relaxed text-muted-foreground">
                    {validationStrategy.intro}
                  </p>
                  <ul className="space-y-4">
                    {validationStrategy.categories.map((c, i) => (
                      <Reveal key={i} delay={i * 0.05}>
                        <li className="flex gap-4">
                          <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/40 border border-primary/20" />
                          <p className="text-[14.5px] leading-relaxed text-muted-foreground">
                            <strong className="font-medium text-foreground">{c.name}</strong> - {c.desc}
                          </p>
                        </li>
                      </Reveal>
                    ))}
                  </ul>
                </div>
              </div>

              <Reveal delay={0.2}>
                <div className="group flex flex-col gap-3 py-6 sm:flex-row sm:gap-8 md:gap-12 md:py-8 border-y border-border">
                  <div className="shrink-0 flex items-center pt-0.5 sm:w-20">
                    <div className="h-1 w-8 bg-primary/40 rounded-full transition-all duration-500 group-hover:w-12 group-hover:bg-primary" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-display text-xl font-semibold tracking-tight text-foreground sm:text-2xl mb-4">
                      Expected Metrics
                    </h4>
                    <p className="text-[15px] leading-relaxed text-muted-foreground max-w-4xl">
                      {validationStrategy.conclusion}
                    </p>
                  </div>
                </div>
              </Reveal>
            </div>
          </Section>

          <Section id="technologies" icon={Layers} title="Technologies Used">
            <div className="space-y-12">
              <p className="text-[16px] leading-relaxed text-muted-foreground w-full">
                Nexar is built as a <strong className="font-medium text-foreground">microservices monorepo</strong> with six independently-deployable services, using a carefully-chosen stack that spans machine learning, quantum SDKs, cloud infrastructure, and modern web development.
              </p>

              <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
                {technologyCategories.map((category, i) => (
                  <Reveal key={category.title} delay={i * 0.05}>
                    <div className="flex flex-col border-t-[3px] border-primary/20 pt-5 transition-colors hover:border-primary group h-full">
                      <h5 className="font-display text-lg font-semibold text-foreground mb-4 group-hover:text-primary transition-colors">
                        {category.title}
                      </h5>
                      <ul className="space-y-3">
                        {category.items.map((item, j) => (
                          <li key={j} className="text-[14px] leading-relaxed text-muted-foreground flex items-start gap-2.5">
                            <span className="mt-2 h-1 w-1 shrink-0 bg-primary/40 rounded-full" />
                            <span>
                              <strong className="font-medium text-foreground block mb-0.5">{item.name}</strong>
                              <span className="text-[13.5px] opacity-90 block">{item.desc}</span>
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </Reveal>
                ))}
              </div>
            </div>
          </Section>
        </div>
      </div>
    </>
  );
}

function Section({ id, icon: Icon, title, children }: { id: string; icon: React.ElementType; title: string; children: React.ReactNode }) {
  return (
    <section id={id} className="scroll-mt-24">
      <Reveal>
        <div className="mb-6 flex items-center gap-3">
          <Icon className="h-5 w-5 text-foreground" strokeWidth={1.6} />
          <h3 className="font-display text-2xl font-semibold sm:text-3xl">{title}</h3>
        </div>
        <div className="space-y-4 text-base leading-relaxed text-muted-foreground">{children}</div>
      </Reveal>
    </section>
  );
}
