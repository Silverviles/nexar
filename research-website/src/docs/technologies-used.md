## Technologies Used

Nexar is built as a **microservices monorepo** with six independently-deployable services, using a carefully-chosen stack that spans machine learning, quantum SDKs, cloud infrastructure, and modern web development.

### Programming Languages

| Language | Usage |
|----------|-------|
| **Python 3.9+** | Core language for all ML models, quantum circuit construction, code analysis, and backend services |
| **Node.js / TypeScript** | API Gateway and inter-service communication layer |
| **JavaScript / TypeScript** | Frontend web interface |

### Machine Learning & AI

| Technology | Usage |
|------------|-------|
| **TensorFlow 2.x** | Neural network models for performance prediction and pattern recognition |
| **PyTorch** | Alternative deep learning framework for select model experiments |
| **Scikit-learn** | Classical ML algorithms and preprocessing pipelines |
| **XGBoost** | Gradient boosting models in the Decision Engine ensemble |
| **CodeBERT** | Pre-trained transformer for code classification across five quantum frameworks |
| **CodeT5-base** | Fine-tuned model for classical-to-quantum code conversion |
| **Graph Neural Networks (GNN)** | Structural pattern detection in AST graphs |

### Quantum Computing Frameworks

| Framework | Role |
|-----------|------|
| **Qiskit** | IBM's quantum SDK — primary framework for circuit construction and Aer simulation |
| **Qiskit Aer** | Noise-aware quantum simulation for performance prediction |
| **Cirq** | Google's quantum library for Cirq-based workloads |
| **Q# (Microsoft QDK)** | Microsoft quantum development kit support |
| **OpenQASM 3.0** | Quantum assembly language with timing, pulse control, and gate modifiers |
| **Forest SDK** | Rigetti quantum computing support |

### Quantum Cloud Providers

| Provider | Integration |
|----------|-------------|
| **IBM Quantum** | Primary quantum backend — 127-qubit Eagle processors and simulators |
| **AWS Braket** | Multi-vendor quantum hardware access |
| **Azure Quantum** | Microsoft's quantum computing service |

### Code Parsing & Analysis

| Tool | Usage |
|------|-------|
| **ANTLR4** | Multi-language parser generator for Qiskit, Q#, Cirq, and OpenQASM |
| **tree-sitter** | AST-based parsing for classical software metrics extraction |
| **Python `ast` module** | Lightweight AST extraction in the AI Code Converter |

### Web Frameworks & APIs

| Technology | Usage |
|------------|-------|
| **FastAPI** | RESTful API implementation for Python-based microservices |
| **Express.js** | JWT-authenticated API Gateway |
| **RESTful APIs** | Unified communication across all microservices |

### Data Storage

| System | Role |
|--------|------|
| **PostgreSQL** | Execution history, decision logs, cost models, and persistent data |
| **Redis** | Real-time data caching for hardware status and pricing feeds |

### DevOps & Deployment

| Technology | Role |
|------------|------|
| **Docker** | Containerization of all microservices |
| **Google Cloud Run** | Serverless container deployment platform |
| **Google Cloud Platform (GCP)** | Primary cloud infrastructure |
| **Terraform** | Infrastructure as Code for reproducible deployments |
| **Git (GitHub/GitLab)** | Version control with CI/CD pipelines |
| **Kubernetes** | Container orchestration support for scaling |

### Testing & Quality

| Tool | Role |
|------|------|
| **Unit testing frameworks** | Component validation with 80%+ code coverage |
| **Integration testing** | End-to-end workflow validation including feedback loops |
| **Performance testing** | Scalability testing under load |
| **Benchmark suite (100 workloads)** | Classical, hybrid, and quantum algorithms for validation |

### Architecture Summary

The complete stack flows as follows:

```
User → React Frontend
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

All containerized with Docker · Deployed on GCP Cloud Run · Managed via Terraform
```