# Nexar — AI Agent Guide

This document describes the essential architecture, workflows, and patterns that AI agents should understand before contributing to the Nexar codebase.

---

## Architecture Overview

**Nexar** is an intelligent quantum-classical code routing platform. It accepts source code, analyzes it across multiple dimensions (language, complexity, quantum suitability), and routes execution to quantum devices, quantum simulators, or classical hardware—all through a unified web interface.

### The Six Microservices

Nexar is a **microservices monorepo** with independently deployable services:

| Service | Port | Stack | Core Responsibility |
|---------|------|-------|---------------------|
| **Frontend** | 5173 | React 18, TypeScript, Vite, Tailwind | User interface for code submission and results |
| **API Gateway** | 3000 | Express 5, TypeScript | Authentication, request routing, logging |
| **Code Analysis Engine** | 8002 | FastAPI, Python | Language detection, complexity metrics, algorithm classification |
| **Decision Engine** | 8003 | FastAPI, Python | ML-based routing decision (quantum vs. classical) |
| **AI Code Converter** | 8001 | FastAPI, Python | Classical-to-quantum code translation |
| **Hardware Abstraction Layer** | 8004 | FastAPI, Python | Provider-agnostic quantum backend interface (IBM, AWS, Azure) |

### Request Flow

1. User submits code via **Frontend** (REST to API Gateway)
2. **API Gateway** authenticates (JWT), assigns request ID, proxies to Code Analysis Engine
3. **Code Analysis Engine** extracts: language, complexity metrics, quantum metrics, algorithm type
4. **Decision Engine** consumes metrics, predicts optimal target (real quantum, simulator, or classical)
5. If quantum: **AI Code Converter** translates Python → Qiskit/Cirq circuits
6. **Hardware Abstraction Layer** submits to selected provider (IBM Qiskit, AWS Braket, Azure Quantum)
7. Results flow back through API Gateway to Frontend

See `docs/architecture/overview.md` and `system-architecture.svg` for visual details.

---

## Critical Developer Workflows

### Starting Development

**All services:** Copy all `.env.example` files to `.env` in their respective directories:
```bash
# Project root
for dir in api ai-code-converter code-analysis-engine decision-engine hardware-abstraction-layer frontend; do
  cp $dir/.env.example $dir/.env 2>/dev/null || true
done
```

**Setup (one-time):** Run the setup script (creates Python venvs, installs deps, downloads ML models):
```bash
bash setup-dev.sh
```

**Start all services:** The orchestration script handles Python venv activation, model downloads, and color-coded logging:
```bash
bash start-dev.sh                    # All services
bash start-dev.sh --no-python        # Only Node services
bash start-dev.sh api frontend       # Specific services
bash start-dev.sh --force-models     # Force re-download ML models from GCS
```

**Quick verify:** Once running, all services expose a root endpoint:
- http://localhost:3000/ (API)
- http://localhost:5173/ (Frontend)
- http://localhost:8001/ (AI Converter)
- http://localhost:8002/ (Code Analysis)
- http://localhost:8003/ (Decision Engine)
- http://localhost:8004/ (HAL)

### Python Services: Structure & Commands

All Python services follow this pattern:

```bash
cd <service-dir>
python -m venv .venv
source .venv/bin/activate              # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --port <PORT> --reload
```

**Special handling:**
- **ai-code-converter** & **code-analysis-engine** download ML models from Google Cloud Storage (GCS) on first startup if `download_model.py` is present. Environment variables control paths:
  - `ai-code-converter`: `MODEL_PATH`, `GCS_MODEL_URI`
  - `code-analysis-engine`: `ML_MODELS_DIR`, `GCS_MODEL_URI`
- **hardware-abstraction-layer** uses `app.main:app` as the entry point (different from others)

### Node Services: Structure & Commands

All Node services follow this pattern:

```bash
cd <service-dir>
npm install
npm run dev        # TypeScript + hot-reload
npm run build      # Production build
```

### Cross-Service HTTP Communication

Services communicate over HTTP. Base URLs are configured in `.env` files and passed through the API Gateway:

```typescript
// api/src/server.ts example
const DECISION_ENGINE_URL = process.env.DECISION_ENGINE_URL || 'http://localhost:8003';
const CODE_ANALYSIS_ENGINE_URL = process.env.CODE_ANALYSIS_ENGINE_URL || 'http://localhost:8002';
```

When adding new inter-service calls, **always use environment variables for URLs**, never hardcode.

---

## Project-Specific Patterns & Conventions

### 1. **FastAPI Services: Logging Bootstrap**

All Python services bootstrap logging **before importing any modules** to ensure Google Cloud Logging integration works when running on Cloud Run (detected via `K_SERVICE` env var):

```python
# This MUST be first in main.py
import logging
import os

if os.getenv("K_SERVICE"):
    import google.cloud.logging
    client = google.cloud.logging.Client()
    client.setup_logging()
else:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# Now safe to import other modules
from fastapi import FastAPI
```

**Why:** Modules that call `logging.getLogger(__name__)` will inherit the configured handler. If logging is set up *after* imports, those modules will still use the default handler.

### 2. **FastAPI Services: CORS Middleware**

All FastAPI services add CORS middleware immediately after app creation:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

This is necessary because the API Gateway proxies requests to backend services, and browsers enforce CORS on those requests.

### 3. **Express API Gateway: Request ID Tracing**

The API Gateway assigns a **unique request ID** to every incoming request for tracing across service calls. This is handled by request middleware and logged at the start of every upstream call.

**When modifying API routes:** Ensure that request IDs are passed through headers to backend services for correlation. Check `@middleware/request-logger.js` for the pattern.

### 4. **Configuration Management**

- **Python:** Use `pydantic_settings.BaseSettings` with `.env` file support. Example: `decision-engine/config/app_config.py`
  ```python
  from pydantic_settings import BaseSettings
  class Settings(BaseSettings):
      APP_NAME: str = "Decision Engine API"
      PORT: int = 8003
      class Config:
          env_file = ".env"
  ```

- **Node:** Use `dotenv` package to load `.env` files at startup (see `api/src/server.ts` line 1: `import "dotenv/config"`).

### 5. **FastAPI Routers: Organization Pattern**

FastAPI services use a `routes/` directory with one router per logical domain:

```
ai-code-converter/
  routes/
    api.py              # Main router, included in main.py
    quantum_analysis.py # Specialized analysis endpoints
```

Routers are created with `APIRouter()` and included in `main.py`:
```python
from routes.api import router as api_router
app.include_router(api_router)
```

### 6. **TypeScript in Node Services**

- **API Gateway** (`/api`) uses TypeScript with path aliases (configured in `tsconfig.json`):
  ```typescript
  import { logger } from '@config/logger.js';  // @ resolves to /src
  ```
  
- **Frontend** (`/frontend`) uses TypeScript with Vite (fast HMR). Build target is `dist/`.

### 7. **Environment Variable Naming Convention**

Each service defines its own config schema with clear env var names:

```
DECISION_ENGINE_URL         # Service URLs (HTTP endpoints)
MODEL_PATH                  # File paths to ML models
GCS_MODEL_URI              # Google Cloud Storage URIs
DATABASE_URL               # Database connection strings
CORS_ORIGINS               # List of allowed origins
LOG_LEVEL                  # Logging verbosity
```

**When adding env vars:** Define them in the service's config file (with defaults), document in `.env.example`, and update `.env` files locally.

### 8. **Docker Builds: Per-Service Dockerfiles**

Each service has its own `Dockerfile` (no multi-stage Docker Compose). When building for deployment:

```bash
docker build -f <service>/Dockerfile -t nexar-<service> <service>/
```

**Cloud deployment:** Built images are pushed to Google Artifact Registry and deployed to Cloud Run via Terraform.

### 9. **ML Model Loading**

- **Code Analysis Engine** and **AI Code Converter** load pre-trained models at startup
- Models are stored in Google Cloud Storage (GCS) and downloaded on first run
- `download_model.py` scripts handle this; they check if models exist locally before downloading
- If download fails, services gracefully degrade with fallback heuristics

**When modifying ML models:** Update the GCS bucket paths and re-run `start-dev.sh --force-models` to refresh.

---

## Integration Points & Data Flow

### Frontend ↔ API Gateway

**Flow:** REST JSON over HTTPS
- **Auth Routes** (public): `/api/v1/auth/` — login, register, verify, OAuth
- **Protected Routes** (require JWT): All backend service proxies

**JWT Token:** Managed by Firebase/Firestore; passed in `Authorization: Bearer <token>` header.

### API Gateway ↔ Backend Services

**Flow:** HTTP JSON (localhost in dev, Cloud Run in prod)
- Routes proxy requests based on path prefix (e.g., `/api/v1/analysis/*` → Code Analysis Engine)
- Request ID is forwarded in headers for tracing
- Timeouts and error handling are applied per service

### Code Analysis Engine → Decision Engine

**Flow:** The analysis engine's response (metrics, algorithm classification) is consumed by the Decision Engine to predict routing.

**Key metrics** (from `code-analysis-engine/models/analysis_result.py`):
- Language, complexity scores, qubit requirements
- Algorithm classification (Grover's, Shor's, QAOA, etc.)
- Quantum suitability level (HIGH / MEDIUM / LOW)

### Decision Engine → Hardware Abstraction Layer

**Flow:** Once a routing decision is made, HAL executes the job on the selected provider (real quantum device, simulator, or classical).

**Metadata endpoints:** Each service exposes model/config metadata at `/api/v1/<service>/metadata` for operator inspection.

---

## Testing & Debugging

### Manual Service Testing

Use the `.http` files included in each service:

```
ai-code-converter/test_main.http
code-analysis-engine/test_main.http
```

Open in VS Code with REST Client extension or a similar tool.

### Health Checks

All services expose a root endpoint (`/`) that returns service metadata:

```bash
curl http://localhost:8002/
```

### Logging

- **Development:** All logs appear in terminal (colored by service via `start-dev.sh`)
- **Production (Cloud Run):** Logs are automatically routed to Google Cloud Logging if `K_SERVICE` env var is set

### Common Issues

1. **"Port already in use"** → Change `--port` flag or set `PORT` env var
2. **"Module not found" (Python)** → Ensure `.venv` is activated and `pip install -r requirements.txt` was run
3. **"Cannot find node_modules"** → Run `npm install` in the service directory
4. **Model download fails** → Network/GCS access issue; services fall back to heuristics
5. **CORS error from frontend** → Ensure API Gateway CORS middleware is configured correctly

---

## Adding New Features: Checklist

When adding a new feature across services:

- [ ] **Frontend** — Update React components in `/src/pages` or `/src/components`; add new hooks if needed
- [ ] **API Gateway** — Add route in `/api/src/routes/`, wire in `server.ts`
- [ ] **Backend Service** — Add endpoint in `routes/api.py` (FastAPI) or `routes/` (Express)
- [ ] **Environment Config** — Add any new env vars to `.env.example` files
- [ ] **Logging** — Use `logger.info()` or `logging.getLogger(__name__)` in Python; `logger.info()` in Node
- [ ] **Testing** — Update `.http` test files; verify manually via `curl` or REST Client
- [ ] **Documentation** — Update relevant files in `/docs/architecture/services/`

---

## Key Files for Reference

- **Architecture:** `docs/architecture/overview.md`, `system-architecture.svg`
- **Setup:** `README.md`, `setup-dev.sh`, `start-dev.sh`
- **Infrastructure:** `terraform/` (Cloud Run, networking, secrets)
- **API Gateway:** `api/src/server.ts` (routing, middleware, logging)
- **Example Config:** `decision-engine/config/app_config.py` (Pydantic settings pattern)

---

## Deployment & Infrastructure

Nexar is deployed to **Google Cloud Platform** using **Terraform**:

- **Containerisation:** Each service has its own `Dockerfile` (built independently)
- **Registry:** Built images pushed to Google Artifact Registry
- **Compute:** Cloud Run (fully managed, scales to zero)
- **IaC:** `terraform/` directory defines all infrastructure (services, networking, IAM, secrets)

**When modifying infrastructure:** Update Terraform files and test locally before merging. The `.github/workflows/` (if present) handles CI/CD.

---

## Quick Reference: Service Ports & URLs (Development)

```
Frontend              → http://localhost:5173
API Gateway           → http://localhost:3000
Code Analysis Engine  → http://localhost:8002
Decision Engine       → http://localhost:8003
AI Code Converter     → http://localhost:8001
Hardware Abstraction  → http://localhost:8004
```

All services are accessible from the API Gateway:
```
POST   /api/v1/analysis/analyze
POST   /api/v1/decision/predict
POST   /api/v1/converter/translate
GET    /api/v1/hardware/devices
```

---

## Questions or Ambiguities?

If a pattern isn't clear after reading this, check:

1. **Similar service** — Look at how another service implements the same pattern
2. **Existing code** — Search the codebase for examples (grep, file search)
3. **Documentation** — Check `docs/architecture/services/` for service-specific details
4. **Codebase structure** — Run `ls -la <service>/` to understand the layout


