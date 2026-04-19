# About

Nexar is an intelligent Quantum-Classical Workload Routing Platform that helps developers automatically decide whether a workload should run on quantum or classical hardware — and routes it to the best backend across IBM Quantum, AWS Braket, and Azure Quantum. This page shares the story behind the project, who built it, and why.

---

## 1. About the Project

**Nexar** (internally project RP 25-26J-484, also known as the **Quantum-Classical Code Router** / QCCR) is a full-stack platform that automates the analysis, classification, and routing of computational workloads across quantum and classical execution backends.

Given a piece of source code, Nexar answers a deceptively simple question: *should this run on classical hardware, a quantum simulator, or a real quantum device — and at what cost?* Behind that answer sits a pipeline of four tightly-integrated components:

- **Code Analysis Engine (CAE)** — parses code across Python, Qiskit, Cirq, Q#, and OpenQASM, and extracts a 16-feature vector describing complexity, entanglement, and NISQ viability.
- **AI Code Converter (ACC)** — uses a fine-tuned CodeT5 model to translate classical Python algorithms into Qiskit quantum circuits when quantum execution is advantageous.
- **Decision Engine (DE)** — combines a machine-learning ensemble (50%), physics-aware rules (35%), and a real-time cost analyzer (15%) through weighted voting to produce a routing recommendation with a confidence score.
- **Hardware Abstraction Layer (HAL)** — submits jobs through a unified API across IBM Quantum, AWS Braket, and Azure Quantum, with intelligent scheduling and real-time monitoring.

The platform has been evaluated across 100 diverse workloads spanning classical computation, hybrid quantum-classical algorithms, and pure quantum circuits — achieving correct routing decisions across all categories with an average pipeline latency of 1.5 seconds and decision inference under 15 ms.

---

## 2. About the Team

Nexar is built by a team of four undergraduate researchers from the **Sri Lanka Institute of Information Technology (SLIIT)**, each owning one major component of the system.

### Research Team

| Member | Student ID | Component |
|--------|-----------|-----------|
| **Siriwardhana A. H. L. T. S.** (Sudaraka Tharindu) | IT22094568 | Hardware Abstraction Layer |
| **Prasad H. G. A. T.** (Ashi) | IT22056870 | Decision Engine |
| **Jayasinghe Y. L.** (Yashodha Lasith) | IT22103840 | Code Analysis Engine |
| **Hettiarachchi S. R.** (Sayun) | IT22128386 | AI Code Converter |

### Supervisors

- **Prof. Nuwan Kodagoda** — Department of Information Technology, SLIIT
- **Dr. Kapila Dissanayaka** — Department of Computer Science and Software Engineering, SLIIT

### Affiliation

All team members are pursuing a **B.Sc. (Hons) in Information Technology specializing in Software Engineering** at the Department of Computer Science and Software Engineering, **Sri Lanka Institute of Information Technology**, Malabe, Sri Lanka.

---

## 3. About the Research

Nexar is an undergraduate dissertation research project (**RP 25-26J-484**) positioned at the intersection of quantum computing, machine learning, and cloud infrastructure.

### Research Contributions

1. **Automated Code Analysis Pipeline** — a multi-dimensional engine that detects five programming frameworks, computes complexity metrics, and classifies algorithms via a three-tier approach combining CodeBERT transformers, ensemble ML, and rule-based pattern matching.
2. **Hybrid Decision Framework** — the first system to unify ML predictions, physics-aware rules, and real-time cost analysis through calibrated weighted voting for quantum-classical routing.
3. **Provider-Agnostic Execution Layer** — a hardware abstraction layer supporting IBM Qiskit, AWS Braket, and Azure Quantum through a single unified API.
4. **Empirical Evaluation** — a comprehensive benchmark across 100 workloads revealing the quantum-classical cost crossover at approximately 50–57 qubits.

### Academic Context

The project runs for one academic year and produces multiple deliverables including individual component dissertations, a consolidated research paper, open-source implementation, and this research website. The team collaborates with faculty research groups in quantum software engineering and draws on SLIIT's high-performance computing infrastructure for model training and benchmarking.

---

## 4. Our Motivation

Quantum computing has moved from the lab into the cloud. IBM, AWS, and Microsoft now offer public access to real quantum processors with tens to hundreds of qubits — yet for most developers, a question still looms: *does my code actually belong on a quantum computer, and can I afford to run it there?*

Today, answering that question is hard. It requires deep expertise in quantum algorithms, intimate knowledge of NISQ-era hardware noise, and constant tracking of rapidly-changing provider pricing. The overhead of transpilation, measurement shots, queue times, and error rates means that for many problems — especially those with polynomial classical solutions — classical execution remains orders of magnitude faster and cheaper. Simply owning