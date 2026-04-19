## Research Objectives

### Main Objective

To design and develop **Nexar** — an end-to-end, intelligent Quantum-Classical Code Router (QCCR) platform that automatically analyzes source code, decides whether each workload should run on quantum or classical hardware, converts the code where beneficial, and routes it to the optimal backend across multiple cloud providers — while jointly optimizing for execution time, monetary cost, and NISQ-era hardware constraints.

The platform is envisioned as a serverless backend analogous to AWS Lambda or Google Cloud Run, but uniquely capable of managing, utilizing, and optimizing quantum hardware for short-term executions in a cost-effective manner.

### Specific Objectives

The main objective is achieved through four component-level objectives, one per sub-system.

#### SO1 — Code Analysis Engine (CAE)

Design and develop a comprehensive, multi-language Code Analysis Engine that automatically inspects, characterizes, and classifies source code segments across heterogeneous quantum programming languages to drive downstream routing decisions.

- Design a **unified multi-language parsing and analysis framework** with AST-based parsers for Python/Qiskit, Q#, Cirq, and OpenQASM, normalized through a language-agnostic intermediate representation (IR).
- Develop **quantum operation detection algorithms** that recognize gates (H, CNOT, T), measurements, qubit allocation/deallocation, and circuit topologies, translating language-specific intrinsics into a standardized operation set.
- Implement **comprehensive complexity analysis modules** covering cyclomatic complexity, classical time/space complexity (Big-O), quantum resource estimates (qubit count, gate depth, circuit width), and parallelization potential.
- Integrate **machine-learning-based pattern recognition** to detect canonical quantum algorithms (Grover's, Shor's, QFT, QAOA, VQE) and classify code suitability for quantum execution.
- Enable **low-latency analysis** suitable for interactive development environments and real-time routing pipelines.

#### SO2 — Decision Engine (DE)

Develop an intelligent Decision Engine that optimally routes workloads between quantum and classical resources using machine-learning-based performance prediction, rule-based validation, and real-time cost-benefit analysis.

- **Core decision model development** — train ML models (Random Forest, XGBoost, Neural Networks in an ensemble) capable of predicting optimal hardware allocation from code analysis features, achieving a minimum of 85% accuracy on benchmark problems.
- **Rule-based validation system** — implement threshold-based rules and compatibility checks that enforce safety constraints and handle clear-cut routing cases deterministically across supported quantum and classical backends.
- **Cost analysis framework** — build a component that consumes live provider pricing, estimates execution time, computes ROI, and enables cost-aware routing within budget categories.
- **System integration and testing** — unify ML, rules, and cost analysis through weighted voting and a Decision Merger with confidence scoring and conflict resolution, then validate improvement over baseline rule-based routing.
- **Evaluation and future-work identification** — conduct systematic evaluation, document performance, and specify extensions for advanced adaptive learning and real-time optimization.

#### SO3 — AI Code Converter (ACC)

Develop an AI-powered code converter that automatically transforms selected classical Python algorithms into Qiskit quantum implementations while predicting quantum advantage for NISQ devices.

- **Large Language Model implementation** — fine-tune the CodeT5-base model on 200–500 curated classical-to-quantum algorithm pairs targeting 5–10 well-defined patterns, achieving 90% conversion accuracy.
- **Pattern recognition system development** — build an AST-based recognition engine backed by a pattern database of 50 algorithmic signatures, reaching 85% accuracy on target pattern detection within classical Python code.
- **Performance prediction module** — use Qiskit Aer simulators with basic noise models to estimate runtime, speedup, and NISQ-viability, targeting 80% accuracy in predicting realistic quantum advantage.
- **System integration and validation** — expose the pipeline through a REST API and web interface, validate on 10 benchmark algorithms against known manual quantum implementations, and implement feedback-based learning using execution results.

#### SO4 — Hardware Abstraction Layer (HAL)

Build a hardware abstraction layer that unifies heterogeneous quantum and classical resources behind a single API and manages their cost-effective, short-term utilization.

- **Develop a standardized set of APIs** — design a unified API layer that abstracts differences between quantum and classical hardware, exposes job submission/monitoring/result retrieval, and supports extensibility for new backends (QPUs, classical clusters, GPUs, cloud instances) without changing upper layers.
- **Implement a decision engine for resource routing** — automatically select the most suitable hardware based on workload characteristics, user-defined constraints, and performance requirements, supporting cost-optimization, performance-optimization, and availability-based routing policies, plus manual override.
- **Develop a resource management framework** — create a scheduler supporting fair-share, Shortest Job First (SJF), and round-robin policies; ensure fault tolerance and automatic failover; implement load balancing; and track usage across quantum and classical backends.
- **Enable real-time resource monitoring** — continuously monitor availability and queue lengths across IBM Quantum, AWS Braket, Azure Quantum, and classical compute, feeding status updates back to the Decision Engine.

### Expected Outcomes

By achieving these objectives, the Nexar platform will deliver:

1. **Multi-language code analysis** covering Python, Qiskit, Q#, Cirq, and OpenQASM, with >85% pattern-recognition accuracy.
2. **Automated classical-to-quantum conversion** with 85%+ conversion accuracy and 90%+ quantum-advantage prediction accuracy on selected algorithm categories.
3. **Intelligent, cost-aware routing decisions** with 85%+ hardware recommendation accuracy, decision latency under 2 minutes, and a feedback loop that continuously retrains the ML model, adjusts rule thresholds, and updates cost models.
4. **Provider-agnostic execution** across IBM Qiskit, AWS Braket, and Azure Quantum with unified APIs, intelligent scheduling, and FaaS-style short-task execution.
5. **An empirical cost-benefit evaluation** across 100 diverse workloads (classical, hybrid, and pure quantum), characterizing the quantum-classical crossover point and demonstrating the platform's practical utility as a decision-support tool for the NISQ era and a readiness-ready infrastructure for the fault-tolerant era to come.