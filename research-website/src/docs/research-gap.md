The Overarching Gap
---
Despite growing accessibility to quantum hardware through providers like IBM Quantum, AWS Braket, and Azure Quantum, there is no end-to-end system that automatically analyzes source code, decides whether quantum or classical execution is optimal, converts the code if needed, and routes it to the right hardware. Existing research tackles individual pieces of this problem in isolation — a code analyzer here, a middleware scheduler there, an ML cost model elsewhere — but none unify them into a single pipeline that a developer can use without deep quantum expertise. Nexar fills this gap by delivering the first fully automated, cost-aware, multi-language quantum-classical routing platform built for the NISQ era.

Component-Level Gaps Addressed by Nexar
---
1. Code Analysis Engine — No unified, multi-language, ML-enhanced quantum code analyzer
Existing tools like QChecker (2023), ScaffCC (2014), Q-PAC (2023), and the High-Performance Compiler for QEC (2022) each handle only narrow slices of quantum code analysis, and none combine machine-learning-based pattern recognition with support for multiple quantum languages (Qiskit, Q#, Cirq, OpenQASM). Developers working with heterogeneous codebases have no single tool that can simultaneously detect quantum-amenable segments, estimate complexity, and adapt to evolving hardware characteristics with low enough latency for real-time use.
2. Decision Engine — No integrated, adaptive, economically aware routing intelligence
Current hybrid systems rely on static rules and predetermined thresholds, optimize for single metrics (time or accuracy, not both), and treat technical performance separately from cost. Prior work such as Tannu & Qureshi's quantum-aware resource management and Salavatov & Palacios's Pilot-Quantum middleware lacks predictive ML, feedback-driven learning, real-time cost analysis with live provider pricing, and multi-objective optimization across cost, performance, and reliability.
3. AI Code Converter — No automated classical-to-quantum translation pipeline
No existing system offers end-to-end automated conversion from classical code into quantum equivalents while preserving functional correctness, targeting quantum advantage, and providing noise-aware performance prediction for NISQ devices. Existing quantum simulators assume ideal conditions, current pattern-recognition tools cannot reliably identify quantum-suitable algorithmic structures, and no tool integrates conversion with feedback-driven optimization based on real execution outcomes.
4. Hardware Abstraction Layer — No provider-agnostic, cost-optimized execution layer
Performance-per-cost in quantum computing is a largely unexplored area. Pilot-Quantum is currently the only middleware that manages both quantum and classical resources, but it relies on long-running jobs that inflate cost on quantum hardware. Existing frameworks also lack a unified API spanning IBM Qiskit, AWS Braket, and Azure Quantum with intelligent queue management (fair-share, SJF, round-robin) that would let a single workload transparently target the most suitable backend.

What Makes Nexar's Approach Novel
Nexar closes these gaps simultaneously by integrating four components into one pipeline:

| Component | Gap It Closes | Novel Contribution |
|-----------|---------------|-------------------|
| **Code Analysis Engine** | Fragmented, single-language static analysis | Multi-language AST parsing + CodeBERT-based ML classification in a unified framework |
| **AI Code Converter** | Manual classical-to-quantum translation | Fine-tuned CodeT5 + noise-aware performance prediction for NISQ devices |
| **Decision Engine** | Static, single-metric, cost-blind routing | Hybrid ML ensemble (50%) + physics-aware rules (35%) + real-time cost analyzer (15%) with feedback-driven retraining |
| **Hardware Abstraction Layer** | Provider lock-in, cost-unaware scheduling | Unified API across IBM/AWS/Azure with fair-share/SJF/round-robin scheduling and FaaS-style short-task execution |