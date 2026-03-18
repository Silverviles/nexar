# Quick Start

Get Nexar running locally in minutes. This guide provides copy-paste commands to launch all services.

## Clone the Repository

```bash
git clone https://github.com/Silverviles/nexar.git
cd nexar
```

## Start All Services

Open six separate terminals and run one command in each:

**Terminal 1 -- API Gateway**

```bash
cd api && npm install && npm run dev
```

**Terminal 2 -- AI Code Converter**

```bash
cd ai-code-converter && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --port 8001 --reload
```

**Terminal 3 -- Code Analysis Engine**

```bash
cd code-analysis-engine && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --port 8002 --reload
```

**Terminal 4 -- Decision Engine**

```bash
cd decision-engine && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --port 8003 --reload
```

**Terminal 5 -- Hardware Abstraction Layer**

```bash
cd hardware-abstraction-layer && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --port 8004 --reload
```

**Terminal 6 -- Frontend**

```bash
cd frontend && npm install && npm run dev
```

!!! note "Windows users"
    Replace `source .venv/bin/activate` with `.venv\Scripts\activate` in the Python service commands.

## Verify

Once all services are running, confirm each endpoint responds:

| Service | Health Check URL | Expected Response |
|---------|-----------------|-------------------|
| API Gateway | [http://localhost:3000/](http://localhost:3000/) | JSON welcome message |
| AI Code Converter | [http://localhost:8001/](http://localhost:8001/) | `{"message": "Hello World"}` |
| Code Analysis Engine | [http://localhost:8002/](http://localhost:8002/) | `{"message": "Hello World"}` |
| Decision Engine | [http://localhost:8003/](http://localhost:8003/) | `{"message": "Hello World"}` |
| Hardware Abstraction Layer | [http://localhost:8004/](http://localhost:8004/) | `{"message": "Hello World"}` |
| Frontend | [http://localhost:5173/](http://localhost:5173/) | React application |

Open [http://localhost:5173/](http://localhost:5173/) in your browser to access the Nexar interface.

## Next Steps

For detailed setup instructions, environment configuration, and troubleshooting, see the [full Setup Guide](setup.md).
