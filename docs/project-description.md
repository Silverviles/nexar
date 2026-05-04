# Nexar — Project Description

## 1. Overview

Nexar is an intelligent quantum-classical code routing platform. It accepts source code from users, analyses it across multiple dimensions (language, complexity, algorithm type, quantum suitability), decides whether the code should run on quantum or classical hardware, optionally converts it between paradigms, and executes it on the most appropriate backend — all through a unified web interface.

The system is built as a **microservices monorepo** with six independently deployable services plus a React frontend, deployed to **Google Cloud Platform** via Terraform.

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                         │
│                         Port 5173                               │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                    API Gateway (Express.js)                       │
│                         Port 3000                                │
│          Authentication · Proxying · Logging · Monitoring        │
└──────┬───────────┬───────────┬───────────────┬──────────────────┘
       │           │           │               │
       ▼           ▼           ▼               ▼
┌────────────┐ ┌──────────┐ ┌────────────┐ ┌─────────────────────┐
│   Code     │ │ Decision │ │ AI Code    │ │ Hardware Abstraction│
│  Analysis  │ │  Engine  │ │ Converter  │ │       Layer         │
│  Engine    │ │          │ │            │ │                     │
│ Port 8002  │ │ Port 8003│ │ Port 8001  │ │     Port 8004       │
│  (FastAPI) │ │ (FastAPI)│ │ (FastAPI)  │ │     (FastAPI)       │
└────────────┘ └──────────┘ └────────────┘ └─────────────────────┘
                                                     │
                                          ┌──────────┼──────────┐
                                          ▼          ▼          ▼
                                       IBM       AWS        Azure
                                      Qiskit    Braket     Quantum
```

### Typical Request Flow

1. A user submits code through the **Frontend**.
2. The **API Gateway** authenticates the request and proxies it to the appropriate backend service.
3. The **Code Analysis Engine** inspects the code — detecting the language, computing complexity metrics, identifying algorithms, and extracting quantum-specific properties.
4. The **Decision Engine** consumes the analysis output and predicts the optimal execution target (quantum device, quantum simulator, or classical hardware).
5. If quantum execution is chosen, the **AI Code Converter** can translate classical Python code into quantum circuits (Qiskit / Cirq).
6. The **Hardware Abstraction Layer** submits the job to the selected provider and returns results.

---

## 3. Services

### 3.1 Frontend

| | |
|---|---|
| **Location** | `/frontend` |
| **Stack** | React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui |
| **Port** | 5173 |

The frontend is a single-page application that provides the user-facing interface for the entire platform. Key capabilities include:

- **Code submission and analysis** — syntax-highlighted editor with real-time results display.
- **Decision visualisation** — presents the routing recommendation (quantum vs. classical) with supporting metrics.
- **Hardware monitoring** — live view of available quantum devices, their status, and specifications.
- **Execution history** — tracks past jobs with results and performance data.
- **AI code conversion** — interface for translating Python to quantum code and analysing quantum suitability.
- **AST pattern analyser** — visual tool for inspecting quantum-amenable patterns in code.

### 3.2 API Gateway

| | |
|---|---|
| **Location** | `/api` |
| **Stack** | Express 5, TypeScript, Axios, Winston |
| **Port** | 3000 |

The gateway is the single entry point for all client requests. It provides:

- **Authentication** — user registration, login, email verification, and Google OAuth, backed by JWT tokens and Firebase/Firestore.
- **Request proxying** — forwards requests to the four Python backend services based on URL path.
- **Logging and monitoring** — assigns a unique request ID to every call, logs upstream response times, and flags slow responses.
- **Protected routes** — all backend service endpoints require a valid JWT; only auth routes are public.

### 3.3 Code Analysis Engine

| | |
|---|---|
| **Location** | `/code-analysis-engine` |
| **Stack** | FastAPI, Python, CodeBERT, scikit-learn, tree-sitter |
| **Port** | 8002 |

This service is the analytical core of the platform. Given a piece of source code, it produces a rich set of metrics used downstream by the Decision Engine:

- **Language detection** — identifies Python, Qiskit, Cirq, Q#, and OpenQASM with confidence scores.
- **Classical metrics** — cyclomatic complexity, nesting depth, loop/conditional counts, and time/space complexity estimation via AST analysis.
- **Quantum metrics** — qubit requirements, circuit depth (via dependency graph), gate counts, superposition and entanglement scoring (via state simulation), and CX gate ratio.
- **Algorithm classification** — a three-tier approach: (1) CodeBERT transformer for semantic multi-label classification, (2) ML ensemble classifier fallback, (3) rule-based pattern matching.
- **Optimisation suggestions** — actionable recommendations with expected improvement estimates covering maintainability, performance, and resource efficiency.

### 3.4 Decision Engine

| | |
|---|---|
| **Location** | `/decision-engine` |
| **Stack** | FastAPI, Python, scikit-learn |
| **Port** | 8003 |

The Decision Engine receives the metrics produced by the Code Analysis Engine and predicts the optimal execution platform. It uses trained ML classification models that consider problem type, complexity, qubit count, gate profile, memory requirements, and time complexity to recommend one of: a real quantum device, a quantum simulator, or classical hardware. The service also exposes model metadata so operators can inspect the active model version and its configuration.

### 3.5 AI Code Converter

| | |
|---|---|
| **Location** | `/ai-code-converter` |
| **Stack** | FastAPI, Python, Transformers, Qiskit, Cirq |
| **Port** | 8001 |

This service bridges the gap between classical and quantum code:

- **Code translation** — converts classical Python into quantum circuits targeting Qiskit or Cirq, using transformer-based code generation.
- **Quantum pattern recognition** — detects patterns amenable to quantum speedup (e.g., linear search → Grover's, optimisation → QAOA, factorisation → Shor's).
- **Suitability scoring** — assigns a quantum suitability level (HIGH / MEDIUM / LOW) with confidence scores and expected speedup estimates.
- **Circuit execution** — runs generated quantum circuits and returns measurement distributions, circuit diagrams, and performance metrics.
- **Logic extraction** — strips boilerplate from submitted code to isolate the core logic function for cleaner analysis.

### 3.6 Hardware Abstraction Layer

| | |
|---|---|
| **Location** | `/hardware-abstraction-layer` |
| **Stack** | FastAPI, Python, Qiskit, Amazon Braket SDK, Azure Quantum SDK |
| **Port** | 8004 |

The HAL provides a provider-agnostic interface to quantum computing backends:

- **Multi-provider support** — IBM Qiskit (real devices and simulators), AWS Braket, and Azure Quantum.
- **Device management** — lists available devices per provider with specifications (qubit count, status, connectivity, gate set).
- **Job execution** — submits quantum circuits or classical code to the selected backend, supporting configurable shot counts.
- **Job lifecycle** — tracks job status, retrieves results, and monitors execution performance.
- **Scheduling and availability** — schedules quantum jobs and checks device availability windows.

---

## 4. Technology Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui, React Router, TanStack Query, Recharts, Zod |
| API Gateway | Express 5, TypeScript, Axios, JWT, bcrypt, Firebase/Firestore, Winston |
| Backend Services | FastAPI, Uvicorn, Pydantic |
| ML / AI | CodeBERT (Transformers), scikit-learn, tree-sitter, AST analysis |
| Quantum | Qiskit, Cirq, Amazon Braket SDK, Azure Quantum SDK |
| Infrastructure | Google Cloud Platform, Terraform, Cloud Run, Artifact Registry |
| Containerisation | Docker (per-service Dockerfiles) |

