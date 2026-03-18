# Nexar

**Intelligent Quantum-Classical Code Routing Platform**

---

Nexar is an intelligent platform that automatically analyzes classical code and determines whether it would benefit from quantum execution. It inspects the structure, complexity, and algorithmic patterns of submitted code, predicts the optimal execution target -- classical or quantum -- and translates the code into quantum circuits when advantageous. Nexar then routes the compiled job to the most suitable quantum hardware provider, abstracting away the complexity of multi-vendor quantum backends.

## Architecture

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

## How It Works

The platform processes each request through a six-step pipeline:

1. **Submit** -- The user submits code through the React frontend.
2. **Route** -- The API Gateway authenticates the request and proxies it to the appropriate backend service.
3. **Analyze** -- The Code Analysis Engine inspects the code for language, complexity metrics, algorithmic patterns, and quantum properties.
4. **Decide** -- The Decision Engine predicts the optimal execution target (classical or quantum) based on the analysis results.
5. **Convert** -- If quantum execution is selected, the AI Code Converter translates the classical Python code into quantum circuits.
6. **Execute** -- The Hardware Abstraction Layer submits the job to the selected quantum provider (IBM Qiskit, AWS Braket, or Azure Quantum).

## Technology Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui |
| API Gateway | Express 5, TypeScript, JWT, Firebase/Firestore |
| Backend Services | FastAPI, Uvicorn, Pydantic |
| ML / AI | CodeBERT, scikit-learn, tree-sitter |
| Quantum | Qiskit, Cirq, Amazon Braket SDK, Azure Quantum SDK |
| Infrastructure | Google Cloud Platform, Terraform, Cloud Run |

## Navigation

- [Getting Started](getting-started/setup.md) -- Set up the development environment
- [Architecture](architecture/overview.md) -- System design and service details
- [Research](research/proposals/index.md) -- Research proposals and findings
- [Full Project Description](project-description.md) -- Complete project specification

## Team

| Member | Component |
|--------|-----------|
| Siriwardhana A H L T S | Hardware Abstraction Layer |
| Hettiarachchi S R | AI Code Converter |
| Jayasinghe Y L | Code Analysis Engine |
| Prasad H G A T | Decision Engine |
