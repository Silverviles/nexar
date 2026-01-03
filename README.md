# Nexar Setup Guide

This guide walks you through setting up and running all services in the Nexar research project. Follow the instructions for each service you need to run.

## Services Overview

This monorepo contains 6 services:
- **ai-code-converter** — Python FastAPI service (port 8001)
- **code-analysis-engine** — Python FastAPI service (port 8002) 
- **decision-engine** — Python FastAPI service (port 8003)
- **api** — TypeScript Express API (port 3000)
- **frontend** — React + Vite web app (port 5173)
- **hardware-abstraction-layer** — Python FastAPI service (port 8004)

## Prerequisites

Install these tools before setting up any service:

- **Node.js** (v18 or higher) - [Download here](https://nodejs.org/)
- **Python** (3.10 or higher) - [Download here](https://python.org/)
- **Git** - [Download here](https://git-scm.com/)

## Setup Instructions

Choose which services you need and follow their setup steps below.

### 1. API Service (TypeScript Express)

The API service provides backend endpoints for the application.

**Step 1:** Navigate to the API directory
```bash
cd api
```

**Step 2:** Install dependencies
```bash
npm install
```

**Step 3:** Start the development server
```bash
npm run dev
```

**Verification:** Visit http://localhost:3000/ - you should see a JSON welcome message.

**Production build (optional):**
```bash
npm run build
npm start
```

**Port:** 3000 (customize with `PORT` environment variable)

### 2. Frontend (React + Vite)

The frontend provides the user interface for the application.

**Step 1:** Navigate to the frontend directory
```bash
cd frontend
```

**Step 2:** Install dependencies
```bash
npm install
```

**Step 3:** Start the development server
```bash
npm run dev
```

**Verification:** Visit http://localhost:5173/ - you should see the React application.

**Production build (optional):**
```bash
npm run build
npm run preview
```

**Port:** 5173 (Vite default)

### 3. Python Services (FastAPI)

Each Python service is a FastAPI application. Follow these steps for each service you need.

#### AI Code Converter (Port 8001)

**Step 1:** Navigate to the service directory
```bash
cd ai-code-converter
```

**Step 2:** Create and activate virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

**Step 3:** Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Step 4:** Start the service
```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

**Verification:** Visit http://localhost:8001/ - you should see `{"message": "Hello World"}`

#### Code Analysis Engine (Port 8002)

**Step 1:** Navigate to the service directory
```bash
cd code-analysis-engine
```

**Step 2:** Create and activate virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

**Step 3:** Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt # This may take a moment :)
```

**Step 4:** Start the service
```bash
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

**Verification:** Visit http://localhost:8002/ - you should see `{"message": "Hello World"}`

#### Decision Engine (Port 8003)

**Step 1:** Navigate to the service directory
```bash
cd decision-engine
```

**Step 2:** Create and activate virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

**Step 3:** Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Step 4:** Start the service
```bash
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

**Verification:** Visit http://localhost:8003/ - you should see `{"message": "Hello World"}`

### 4. Hardware Abstraction Layer (Port 8004)

**Step 1:** Navigate to the service directory
```bash
cd hardware-abstraction-layer
```

**Step 2:** Create and activate virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

**Step 3:** Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Step 4:** Start the service
```bash
uvicorn main:app --host 127.0.0.1 --port 8004 --reload
```

**Verification:** Visit http://localhost:8004/ - you should see `{"message": "Hello World"}`

**Verification:** You should see "{"status":"running"}" printed to the console.

## Running Multiple Services

To run the full application, start services in separate terminals in this order:

1. **Start the API** (Terminal 1)
2. **Start Python services** (Terminals 2-4) - only the ones you need
3. **Start the frontend** (Terminal 5)
4. **Start the HAL** (Terminal 6)

## Quick Start Commands

Copy and paste these commands in separate terminals:

**Terminal 1 - API:**
```bash
cd api && npm install && npm run dev
```

**Terminal 2 - AI Code Converter:**
```bash
cd ai-code-converter && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --port 8001 --reload
```

**Terminal 3 - Code Analysis Engine:**
```bash
cd code-analysis-engine && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --port 8002 --reload
```

**Terminal 4 - Decision Engine:**
```bash
cd decision-engine && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --port 8003 --reload
```

**Terminal 5 - Frontend:**
```bash
cd frontend && npm install && npm run dev
```

**Terminal 6 - Hardware Abstraction Layer:**
```bash
cd hardware-abstraction-layer && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --port 8004 --reload
```

## Port Summary

- API: http://localhost:3000/
- AI Code Converter: http://localhost:8001/
- Code Analysis Engine: http://localhost:8002/
- Decision Engine: http://localhost:8003/
- Hardware Abstraction Layer: http://localhost:8004/
- Frontend: http://localhost:5173/

## Troubleshooting

**Port already in use:**
- Change the port by modifying the `--port` flag for Python services
- Set `PORT` environment variable for the API: `PORT=3001 npm run dev`

**Python virtual environment issues:**
- Make sure you activate the virtual environment: `source .venv/bin/activate`
- On Windows use: `.venv\Scripts\activate`

**Missing dependencies:**
- Run `npm install` in Node.js services (api, frontend)
- Run `pip install -r requirements.txt` in Python services

**TypeScript errors:**
- Ensure you're in the correct directory
- Try deleting `node_modules` and running `npm install` again