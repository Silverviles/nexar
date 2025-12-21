# Project Overview

This project is a **Hardware Abstraction Layer (HAL)** microservice built with **FastAPI**. It acts as a unified gateway for interacting with both **Quantum Computing** platforms (IBM Quantum, AWS Braket, Azure Quantum) and **Classical Compute** providers (IBM Cloud Functions, AWS Lambda, Azure Functions).

The system allows upstream applications (like code converters or routers) to submit tasks without needing to manage specific SDKs, authentication details, or execution logic for each provider. It now includes intelligent **Job Management** for batching and priority scheduling.

**Main Technologies:**

*   **Framework:** FastAPI (Python)
*   **Server:** Uvicorn
*   **Quantum SDKs:** Qiskit (IBM), (Placeholders for Boto3/AWS, Azure Quantum)
*   **Classical SDKs:** `ibm-cloud-sdk-core` (IBM Cloud Functions)
*   **Configuration:** Pydantic Settings (`.env` support)
*   **Testing:** Pytest

# Architecture

The application is structured into the following layers:

1.  **API Layer (`app/api/`)**:
    *   Exposes REST endpoints for Quantum (`/api/quantum/...`) and Classical (`/api/classical/...`) execution.
    *   Handles job status checking and result retrieval.
    *   Validates requests using Pydantic models.

2.  **Service Layer (`app/services/`)**:
    *   **`compute_service.py`**: The central registry and dispatcher. It manages a collection of `BaseProvider` instances and routes requests to the correct one based on the provider name.
    *   **`job_manager.py`**: Handles **Job Scheduling**.
        *   **Priority Queueing**: "High" priority jobs bypass the queue. "Standard" priority jobs are buffered.
        *   **Batch Optimization**: Groups standard jobs into batches based on **Time** (flush every X seconds) or **Cost** (flush when batch size reaches N).
    *   **`factory.py`**: Responsible for wiring up the services and registering all available providers.

3.  **Provider Layer (`app/providers/`)**:
    *   **`base.py`**: Defines the abstract base classes `QuantumProvider` and `ClassicalProvider` (inheriting from `BaseProvider`).
    *   **Quantum Implementations**:
        *   `ibm_quantum.py`: Fully functional IBM Qiskit implementation with batching support via `Sampler` primitives.
        *   `aws_quantum.py`, `azure_quantum.py`: Skeleton implementations.
    *   **Classical Implementations**:
        *   `ibm_classical.py`: Executes Python scripts on IBM Cloud Functions (Serverless).
        *   `local.py`: Executes Python scripts locally (for testing/dev).
        *   `aws_classical.py`, `azure_classical.py`: Skeleton implementations.

4.  **Models (`app/models/`)**:
    *   `execution.py`: Models for `JobRequest`, `JobSubmission`, `JobPriority`, `OptimizationStrategy`.
    *   `quantum_models.py`: `QuantumCircuit` (QASM).
    *   `classical_models.py`: `ClassicalTask` (Python code).

# Building and Running

1.  **Prerequisites**:
    *   Python 3.9+
    *   Virtual Environment (recommended)

2.  **Setup**:
    ```powershell
    # Create and activate venv
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1

    # Install dependencies
    pip install -r requirements.txt
    ```

3.  **Configuration**:
    *   Create a `.env` file in the root directory.
    *   Add necessary credentials (optional for Local/Mock, required for Real Providers):
        ```env
        IBM_QUANTUM_TOKEN=your_ibm_token
        IBM_CLOUD_API_KEY=your_ibm_cloud_api_key
        ```

4.  **Run Application**:
    ```powershell
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    *   API Docs: `http://127.0.0.1:8000/docs`

5.  **Run Tests**:
    ```powershell
    python -m pytest
    ```

# Development Conventions

*   **Provider Pattern**: All new hardware backends must inherit from `QuantumProvider` or `ClassicalProvider` and be registered in `app/services/factory.py`.
*   **Batching**: Providers should override `execute_batch` if they support optimized group execution. The default implementation loops sequentially.
*   **Async First**: The `JobManager` runs a background thread for monitoring queues.
*   **Safety**: The `LocalClassicalProvider` executes arbitrary code locally. It is intended for development only.
*   **Testing**: Use `unittest.mock` to mock external API calls (IBM, AWS, etc.) to ensure tests are fast and don't require real credentials.
