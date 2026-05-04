# System Overview

Nexar is an intelligent quantum-classical code routing platform that analyses user-submitted code, determines whether it should run on a quantum device, a quantum simulator, or a classical machine, and executes it on the most appropriate backend. The platform is built as a microservices monorepo deployed on Google Cloud Platform.

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

## Microservices Layout

The Nexar monorepo contains six independently deployable services. Each service owns its own Dockerfile, dependency manifest, and configuration, allowing teams to develop, test, and release each component on its own cadence. Inter-service communication happens over HTTP, with the API Gateway acting as the sole ingress point for external traffic and routing requests to the appropriate backend service.

| Service | Directory | Port | Stack | Purpose |
|---------|-----------|------|-------|---------|
| Frontend | `/frontend` | 5173 | React 18, TypeScript, Vite | User interface for code submission, analysis, and results |
| API Gateway | `/api` | 3000 | Express 5, TypeScript | Authentication, request proxying, logging |
| Code Analysis Engine | `/code-analysis-engine` | 8002 | FastAPI, Python | Language detection, complexity analysis, algorithm classification |
| Decision Engine | `/decision-engine` | 8003 | FastAPI, Python | ML-based quantum vs. classical routing |
| AI Code Converter | `/ai-code-converter` | 8001 | FastAPI, Python | Classical-to-quantum code translation |
| Hardware Abstraction Layer | `/hardware-abstraction-layer` | 8004 | FastAPI, Python | Provider-agnostic quantum backend interface |

## Request Flow

A typical request passes through the platform in six steps:

1. **Code Submission** -- The user writes or pastes code into the Frontend editor and submits it for analysis. The Frontend sends the code to the API Gateway over HTTPS.

2. **Authentication and Routing** -- The API Gateway validates the user's JWT, attaches a unique request ID for tracing, and forwards the payload to the Code Analysis Engine.

3. **Code Analysis** -- The Code Analysis Engine detects the programming language, computes classical metrics (cyclomatic complexity, nesting depth, time/space complexity), extracts quantum metrics (qubit requirements, circuit depth, gate counts), and classifies the algorithm using a three-tier approach (CodeBERT transformer, ML ensemble fallback, rule-based pattern matching). The resulting analysis report is returned to the API Gateway.

4. **Routing Decision** -- The API Gateway forwards the analysis report to the Decision Engine, which builds a feature vector from the metrics and runs it through a trained classification model. The model outputs the optimal execution target: a real quantum device, a quantum simulator, or a classical machine.

5. **Code Conversion and Execution** -- If the decision targets a quantum backend and the submitted code is classical, the API Gateway sends it to the AI Code Converter, which translates it into a quantum circuit (Qiskit or Cirq). The resulting circuit (or the original code, if already quantum) is then submitted to the Hardware Abstraction Layer, which dispatches the job to the selected provider (IBM Qiskit, AWS Braket, or Azure Quantum).

6. **Results Delivery** -- Execution results, including measurement distributions and performance metrics, flow back through the API Gateway to the Frontend, where they are rendered alongside the analysis report and routing rationale.

## Deployment

Nexar is deployed on **Google Cloud Platform** using **Cloud Run** for each service. Infrastructure is managed as code with **Terraform**, with all configuration stored in the `/terraform` directory at the repository root.

- **Containerisation** -- Every service has its own Dockerfile. Images are built in CI and pushed to **Google Artifact Registry**.
- **CI/CD** -- GitHub Actions workflows lint, test, build, and deploy each service independently. Pull requests trigger preview deployments; merges to main trigger production deployments.
- **Infrastructure as Code** -- Terraform modules define Cloud Run services, networking, IAM policies, and secret management, ensuring reproducible environments across staging and production.
