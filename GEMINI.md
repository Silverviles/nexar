# Project Overview

**Nexar** is a research project designed as a **Quantum-Classical Hybrid Computing Platform**. It facilitates the intelligent routing and execution of code on either quantum or classical hardware based on algorithmic characteristics.

The system is a monorepo comprising six distinct microservices that work together to analyze code, make execution decisions, and interface with hardware providers.

## Architecture

The ecosystem consists of the following services:

| Service | Technology | Port | Description |
| :--- | :--- | :--- | :--- |
| **Frontend** | React + Vite (TypeScript) | `5173` | User interface for monitoring jobs, viewing analysis, and managing configuration. |
| **API** | Node.js + Express (TypeScript) | `3000` | Central backend API gateway that orchestrates communication between the frontend and Python microservices. |
| **AI Code Converter** | Python (FastAPI) | `8001` | Converts natural language or legacy code into executable quantum/classical code. |
| **Code Analysis Engine** | Python (FastAPI) | `8002` | Analyzes code structure to extract features (gates, depth, complexity) for decision making. |
| **Decision Engine** | Python (FastAPI) | `8003` | Uses ML models to predict the optimal hardware (Quantum vs. Classical) for a given task. |
| **Hardware Abstraction Layer (HAL)** | Python (FastAPI) | `8004` | Unified gateway for executing jobs on external providers (IBM Quantum, AWS, Azure, etc.). |

## Service Details

### 1. Frontend (`frontend/`)
A modern React application built with Vite and TypeScript. It uses `shadcn/ui` components and Tailwind CSS for styling.
- **Key Features:** Dashboard for job monitoring, results visualization, and system configuration.
- **Tech Stack:** React, Vite, TypeScript, Tailwind CSS, TanStack Query, React Router.

### 2. API Gateway (`api/`)
The primary entry point for the frontend, handling authentication (implied), request routing, and aggregation of data from the Python microservices.
- **Tech Stack:** Node.js, Express, TypeScript.

### 3. AI Code Converter (`ai-code-converter/`)
*Service description inferred:* Likely uses LLMs or rule-based systems to translate inputs into QASM (Quantum Assembly) or Python code suitable for execution.

### 4. Code Analysis Engine (`code-analysis-engine/`)
Analyzes input code to determine static properties such as:
- Circuit depth and gate counts (for Quantum).
- Time/Space complexity (for Classical).

### 5. Decision Engine (`decision-engine/`)
The "brain" of the router.
- **Input:** Analysis metrics from the Code Analysis Engine.
- **Logic:** Uses pre-trained Machine Learning models (stored in `ml_models/`) to classify tasks.
- **Output:** Recommendation (Quantum vs. Classical) with confidence scores.

### 6. Hardware Abstraction Layer (`hardware-abstraction-layer/`)
Standardizes execution across different backends.
- **Providers:** IBM Quantum (Qiskit), IBM Cloud Functions, and local simulators.
- **Features:** Job batching, priority queuing, and cost estimation.

# Building and Running

## Prerequisites
- **Node.js**: v18+
- **Python**: v3.10+
- **Git**

## Quick Start (All Services)

To run the full system, you will need to start each service in a separate terminal window.

### 1. API Service
```bash
cd api
npm install
npm run dev
# Runs on http://localhost:3000
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

### 3. AI Code Converter
```bash
cd ai-code-converter
python -m venv .venv
# Activate venv: source .venv/bin/activate (Linux/Mac) or .venv\Scripts\activate (Windows)
pip install -r requirements.txt
uvicorn main:app --port 8001 --reload
# Runs on http://localhost:8001
```

### 4. Code Analysis Engine
```bash
cd code-analysis-engine
python -m venv .venv
# Activate venv
pip install -r requirements.txt
uvicorn main:app --port 8002 --reload
# Runs on http://localhost:8002
```

### 5. Decision Engine
```bash
cd decision-engine
./manage.sh setup # Or manual setup
./manage.sh run
# Runs on http://localhost:8003
```

### 6. Hardware Abstraction Layer (HAL)
```bash
cd hardware-abstraction-layer
python -m venv .venv
# Activate venv
pip install -r requirements.txt
uvicorn main:app --port 8004 --reload
# Runs on http://localhost:8004
```

# Development Conventions

- **Environment Variables:** Most services require a `.env` file. Use `.env.example` or `example.env` as a template.
- **Python Virtual Environments:** Always use a virtual environment (`.venv`) for Python services to isolate dependencies.
- **FastAPI:** All Python microservices use FastAPI. The standard entry point is `main.py` (app instance `app`).
- **TypeScript:** Both the API and Frontend use TypeScript. Ensure strict type checking is enabled.
- **Ports:** Strict port assignment is used to avoid conflicts. Do not change default ports unless necessary, and update dependent services if you do.

## Testing
- **Python:** `pytest` is the standard runner.
- **Frontend/API:** Check `package.json` for scripts (currently `npm run lint` for frontend).

## Directory Structure
- `src/` (JS/TS) or `app/` (Python) usually contains the source code.
- `routes/` or `api/` folders contain endpoint definitions.
- `services/` folders contain business logic.
