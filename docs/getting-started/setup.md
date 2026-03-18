# Setup Guide

This guide walks through setting up and running all services in the Nexar platform.

## Prerequisites

Before starting, ensure the following tools are installed:

- **Node.js** v18 or higher -- [Download](https://nodejs.org/)
- **Python** 3.10 or higher -- [Download](https://python.org/)
- **Git** -- [Download](https://git-scm.com/)

## Service Setup

Select a tab below to see setup instructions for each service.

=== "API Gateway"

    Navigate to the API directory and install dependencies:

    ```bash
    cd api
    npm install
    ```

    Start the development server:

    ```bash
    npm run dev
    ```

    **Verify:** Open [http://localhost:3000/](http://localhost:3000/) -- you should see a JSON welcome message.

    **Production build (optional):**

    ```bash
    npm run build
    npm start
    ```

=== "Frontend"

    Navigate to the frontend directory and install dependencies:

    ```bash
    cd frontend
    npm install
    ```

    Start the development server:

    ```bash
    npm run dev
    ```

    **Verify:** Open [http://localhost:5173/](http://localhost:5173/) -- you should see the React application.

    **Production build (optional):**

    ```bash
    npm run build
    npm run preview
    ```

=== "AI Code Converter"

    Navigate to the service directory and create a virtual environment:

    ```bash
    cd ai-code-converter
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    ```

    Install dependencies:

    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

    Start the service:

    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8001 --reload
    ```

    **Verify:** Open [http://localhost:8001/](http://localhost:8001/) -- you should see `{"message": "Hello World"}`.

=== "Code Analysis Engine"

    Navigate to the service directory and create a virtual environment:

    ```bash
    cd code-analysis-engine
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    ```

    Install dependencies:

    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

    Start the service:

    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8002 --reload
    ```

    **Verify:** Open [http://localhost:8002/](http://localhost:8002/) -- you should see `{"message": "Hello World"}`.

=== "Decision Engine"

    Navigate to the service directory and create a virtual environment:

    ```bash
    cd decision-engine
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    ```

    Install dependencies:

    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

    Start the service:

    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8003 --reload
    ```

    **Verify:** Open [http://localhost:8003/](http://localhost:8003/) -- you should see `{"message": "Hello World"}`.

=== "Hardware Abstraction Layer"

    Navigate to the service directory and create a virtual environment:

    ```bash
    cd hardware-abstraction-layer
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    ```

    Install dependencies:

    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

    Start the service:

    ```bash
    uvicorn main:app --host 127.0.0.1 --port 8004 --reload
    ```

    **Verify:** Open [http://localhost:8004/](http://localhost:8004/) -- you should see `{"message": "Hello World"}`.

## Port Summary

| Service | Port | URL |
|---------|------|-----|
| API Gateway | 3000 | [http://localhost:3000/](http://localhost:3000/) |
| Frontend | 5173 | [http://localhost:5173/](http://localhost:5173/) |
| AI Code Converter | 8001 | [http://localhost:8001/](http://localhost:8001/) |
| Code Analysis Engine | 8002 | [http://localhost:8002/](http://localhost:8002/) |
| Decision Engine | 8003 | [http://localhost:8003/](http://localhost:8003/) |
| Hardware Abstraction Layer | 8004 | [http://localhost:8004/](http://localhost:8004/) |

## Running Order

To run the full application, start services in separate terminals in the following order:

1. **API Gateway** (Terminal 1)
2. **Python backend services** (Terminals 2--5) -- start whichever services you need
3. **Frontend** (Terminal 6)

The frontend depends on the API Gateway, which in turn proxies requests to the backend services. Start the API Gateway first so downstream services are available when the frontend loads.

## Troubleshooting

**Port already in use**

- For Python services, change the port with the `--port` flag: `uvicorn main:app --port 8005 --reload`
- For the API Gateway, set the `PORT` environment variable: `PORT=3001 npm run dev`

**Python virtual environment issues**

- Ensure the virtual environment is activated: `source .venv/bin/activate`
- On Windows, use `.venv\Scripts\activate` instead

**Missing dependencies**

- For Node.js services (api, frontend), run `npm install`
- For Python services, run `pip install -r requirements.txt`

**TypeScript errors**

- Confirm you are in the correct directory
- Delete `node_modules` and run `npm install` again
