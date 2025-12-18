# Project Overview

This project is a FastAPI-based microservice that acts as a Hardware Abstraction Layer (HAL) for quantum computing platforms. It provides a unified interface to interact with various quantum SDKs, allowing for platform-agnostic quantum program execution and management.

**Main Technologies:**

*   **Backend Framework:** FastAPI
*   **ASGI Server:** Uvicorn
*   **Quantum SDKs:**
    *   Qiskit (for IBM Quantum)
    *   Azure Quantum
    *   Boto3 (for Amazon Braket)
*   **Language:** Python

**Architecture:**

The application is structured into the following main components:

*   **`app/main.py`**: The main FastAPI application entry point.
*   **`app/api/routes.py`**: Defines the API endpoints for interacting with the quantum providers.
*   **`app/services/quantum_service.py`**: A service class that manages the different quantum providers and orchestrates the quantum operations.
*   **`app/services/factory.py`**: A factory for creating and configuring the `QuantumService`.
*   **`app/providers/`**: Contains the concrete implementations for each quantum provider (IBM, AWS, Azure).
*   **`app/models/`**: Contains the Pydantic models for the API requests and responses.

# Building and Running

1.  **Create and activate a virtual environment:**

    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    ```

2.  **Install dependencies:**

    ```powershell
    pip install -r requirements.txt
    ```

3.  **Run the application:**

    ```powershell
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

The API will be available at `http://127.0.0.1:8000`, and the interactive OpenAPI documentation can be accessed at `http://127.0.0.1:8000/docs`.

# Development Conventions

*   **Providers:** New quantum providers should inherit from the `QuantumProvider` abstract base class in `app/providers/base.py` and implement the required methods.
*   **Configuration:** Application settings should be added to `app/core/config.py`.
*   **Dependencies:** New runtime dependencies should be pinned in `requirements.txt`.
*   **Testing:** Tests are not yet implemented but should be created using `pytest` under the `tests/` directory.
