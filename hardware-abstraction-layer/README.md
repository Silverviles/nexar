# Quantum Hardware Abstraction Layer — FastAPI microservice

This repository hosts a FastAPI-based microservice acting as a Hardware Abstraction Layer (HAL) for quantum computing platforms. It enables a unified interface to interact with various quantum SDKs, allowing for platform-agnostic quantum program execution and management.

- Framework: FastAPI
- ASGI server: Uvicorn
- Dependencies are listed in `requirements.txt`

## Key Features

This HAL provides a standardized way to interact with different quantum computing providers, abstracting away their specific SDKs. Currently supported providers include:

*   **IBM Qiskit:** Interface for IBM Quantum Experience devices and simulators.
*   **AWS Braket:** Interface for Amazon's quantum computing service.
*   **Azure Quantum:** Interface for Microsoft's Azure Quantum platform.

The HAL allows for:

*   Listing available quantum devices from each provider.
*   Executing quantum circuits on specified devices (simulators or real hardware).
*   Monitoring the status of submitted quantum jobs.
*   Retrieving results from completed quantum jobs.

## Quick start (Windows / PowerShell)

1. Create a virtual environment (if you don't already have one):

```powershell
python -m venv .venv
```

2. Activate the virtual environment (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
# or for cmd.exe: .\.venv\Scripts\activate.bat
```

Note: On some systems PowerShell's execution policy prevents running scripts. If you get an execution policy error, you can temporarily allow the script for the current session:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Run the app with Uvicorn (development mode with hot reload):

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8004
```

The API will be available at: http://127.0.0.1:8000
Interactive OpenAPI docs: http://127.0.0.1:8000/docs

## Available endpoints

- GET /
  - Returns: { "status": "running" }
  - Simple root status endpoint.

- GET /api/health
  - Returns: { "status": "ok" }
  - Health-check for the service.

- GET /quantum/providers
  - Returns: { "providers": ["aws", "azure", "ibm"] }
  - Lists the names of all registered quantum providers.

- GET /quantum/{provider_name}/devices
  - Parameters: `provider_name` (path parameter, e.g., "aws", "azure", "ibm")
  - Returns: A list of available quantum devices for the specified provider, each with details like `name`, `qubits`, `provider`, `status`, and `other_info`.

- POST /quantum/{provider_name}/execute
  - Parameters:
    - `provider_name` (path parameter)
    - `circuit` (request body, JSON object representing the quantum circuit, e.g., `{"qasm": "OPENQASM 2.0; include \"qelib1.inc\"; qreg q[2]; creg c[2]; h q[0]; cx q[0],q[1]; measure q[0] -> c[0]; measure q[1] -> c[1];"}`)
    - `device_name` (query parameter, e.g., "simulator", "ibmq_qasm_simulator")
    - `shots` (query parameter, integer, default: 1024)
  - Returns: { "job_id": "..." }
  - Submits a quantum circuit for execution on a specified device.

- GET /quantum/jobs/{provider_name}/{job_id}
  - Parameters:
    - `provider_name` (path parameter)
    - `job_id` (path parameter)
  - Returns: { "status": "..." }
  - Retrieves the current status of a quantum job.

- GET /quantum/jobs/{provider_name}/{job_id}/result
  - Parameters:
    - `provider_name` (path parameter)
    - `job_id` (path parameter)
  - Returns: { "result": { ... } }
  - Retrieves the results of a completed quantum job.

Example (PowerShell):

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/health -Method GET
# or using curl (PowerShell or WSL):
curl http://127.0.0.1:8000/api/health

# Example: Get list of providers
curl http://127.0.0.1:8000/quantum/providers

# Example: (Conceptual) Execute a circuit - requires actual circuit data and device
# Invoke-RestMethod -Uri "http://127.0.0.1:8000/quantum/aws/execute?device_name=simulator&shots=100" `
#   -Method POST `
#   -Headers @{"Content-Type"="application/json"} `
#   -Body '{"qasm": "OPENQASM 2.0; include \"qelib1.inc\"; qreg q[2]; creg c[2]; h q[0]; cx q[0],q[1]; measure q[0] -> c[0]; measure q[1] -> c[1];"}'
```

## Project layout

app/
- main.py           — FastAPI application instance and router registration
- api/
  - __init__.py
  - routes.py       — API router and quantum-related endpoints
- core/config.py    — configuration placeholder
- models/
  - __init__.py
  - quantum_models.py — Pydantic models for quantum domain objects
- providers/
  - __init__.py
  - base.py         — Abstract base class for quantum providers
  - aws.py          — AWS Braket provider implementation (TODO)
  - azure.py        — Azure Quantum provider implementation (TODO)
  - ibm.py          — IBM Qiskit provider implementation (TODO)
- services/
  - __init__.py
  - factory.py      — Factory for initializing and configuring QuantumService and providers
  - quantum_service.py — Service for managing and interacting with quantum providers

requirements.txt — pinned dependencies for the project

## Development notes

- `app/core/config.py` is a configuration placeholder. Add application settings (e.g., environment, secrets, connection strings) here using environment variables or pydantic settings.
- Add additional routers under `app/api/` and register them in `app/main.py` with `app.include_router(...)`.
- When adding runtime dependencies, pin them in `requirements.txt` and update any CI that installs dependencies.

## Testing

- There are no automated tests included by default. To add tests, create pytest-based test files under `tests/` and run `pytest` from the repository root.

## Troubleshooting

- If Uvicorn fails to import `app.main:app`, verify you are running the command from the repository root and your virtual environment is activated.
- If dependency installation fails, ensure pip is up-to-date: `python -m pip install --upgrade pip`.

## Contributing

Small fixes, documentation enhancements, and additional endpoints are welcome. Open a pull request with a description of the change.

---
