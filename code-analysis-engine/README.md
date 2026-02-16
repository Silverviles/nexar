# Code Analysis Engine

A FastAPI-based microservice for analyzing quantum and classical code in the Nexar Quantum-Classical Code Router system. This service detects programming languages, parses code, performs both quantum and classical code analysis, uses ML to detect quantum algorithms in the code and extracts quantum circuit metrics for intelligent routing decisions.

## Overview

The Code Analysis Engine receives code submissions and performs comprehensive analysis including:

- Multi-language detection (Python, Qiskit, Cirq, Q#, OpenQASM)
- AST-based complexity analysis
- Quantum circuit metrics extraction
- Algorithm detection (ML + rule-based)
- State simulation for superposition/entanglement scoring

## Architecture

```
code-analysis-engine/
├── models/                 # Pydantic models
│   ├── __init__.py
│   ├── analysis_result.py  # Response schemas
│   └── unified_ast.py      # AST representation
├── modules/                # Analysis components
│   ├── language_detector.py        # Language identification
│   ├── ast_builder.py              # Unified AST construction
│   ├── complexity_analyzer.py      # Classical complexity
│   ├── quantum_analyzer.py         # Quantum metrics
│   ├── algorithm_detector.py       # Pattern-based detection
│   ├── ml_algorithm_classifier.py  # ML-based classification
│   ├── accurate_time_complexity.py # Time complexity analysis
│   ├── accurate_circuit_depth.py   # Circuit depth calculation
│   ├── space_complexity_analyzer.py# Space complexity
│   ├── quantum_state_simulator.py  # State simulation
│   └── parsers/                    # Language-specific parsers
├── datasets/               # Training data
│   └── dataset_generator.py
├── tests/                  # Unit tests
│   ├── test_full_analysis.py
│   ├── test_language_detector.py
│   └── sample_codes/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── run_complete_pipeline.py# Full analysis pipeline runner
└── README.md              # This file
```

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Quick Start

### 1. Setup Environment

```bash
cd code-analysis-engine

# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Service

```bash
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

The service will be available at:

- **API Root**: http://localhost:8002/api/v1/code-analysis-engine/
- **API Docs**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc
- **Health Check**: http://localhost:8002/api/v1/code-analysis-engine/health

### 3. Production Deployment

```bash
# Using uvicorn with multiple workers
uvicorn main:app --host 0.0.0.0 --port 8002 --workers 4

# Using gunicorn with uvicorn workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8002
```

## API Endpoints

### Core Endpoints

| Method | Endpoint                                           | Description                   |
| ------ | -------------------------------------------------- | ----------------------------- |
| GET    | `/api/v1/code-analysis-engine/`                    | Service info and capabilities |
| GET    | `/api/v1/code-analysis-engine/health`              | Health check                  |
| POST   | `/api/v1/code-analysis-engine/detect-language`     | Detect programming language   |
| POST   | `/api/v1/code-analysis-engine/analyze`             | Complete code analysis        |
| GET    | `/api/v1/code-analysis-engine/supported-languages` | List supported languages      |

---

### GET `/api/v1/code-analysis-engine/`

Returns service information and capabilities.

**Response:**

```json
{
  "service": "Code Analysis Engine",
  "version": "1.0.0",
  "status": "operational",
  "capabilities": [
    "Multi-language parsing",
    "Accurate complexity analysis (AST-based)",
    "Quantum metrics extraction (state simulation)",
    "Algorithm detection (pattern matching)",
    "Circuit depth analysis (dependency graph)"
  ]
}
```

---

### GET `/api/v1/code-analysis-engine/health`

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "service": "code-analysis-engine"
}
```

---

### POST `/api/v1/code-analysis-engine/detect-language`

Detect the programming language of submitted code.

**Request Body:**

```json
{
  "code": "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)"
}
```

**Response:**

```json
{
  "language": "qiskit",
  "confidence": 0.95,
  "is_supported": true,
  "details": "Detected Qiskit quantum framework"
}
```

---

### POST `/api/v1/code-analysis-engine/analyze`

Complete code analysis pipeline. Returns metrics for the Decision Engine.

**Request Body:**

```json
{
  "code": "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\nqc.measure_all()"
}
```

**Response (Quantum Code):**

```json
{
  "detected_language": "qiskit",
  "language_confidence": 0.95,
  "problem_type": "search",
  "problem_size": 4,
  "classical_metrics": null,
  "quantum_metrics": {
    "qubits_required": 2,
    "circuit_depth": 3,
    "gate_count": 4,
    "single_qubit_gates": 2,
    "two_qubit_gates": 1,
    "cx_gate_count": 1,
    "cx_gate_ratio": 0.25,
    "measurement_count": 2,
    "superposition_score": 1.0,
    "entanglement_score": 0.75,
    "has_superposition": true,
    "has_entanglement": true,
    "quantum_volume": null,
    "estimated_runtime_ms": null
  },
  "qubits_required": 2,
  "circuit_depth": 3,
  "gate_count": 4,
  "cx_gate_ratio": 0.25,
  "superposition_score": 1.0,
  "entanglement_score": 0.75,
  "time_complexity": "O(sqrt(n))",
  "memory_requirement_mb": 0.5,
  "is_quantum": true,
  "confidence_score": 0.9,
  "analysis_notes": "Quantum analysis: qiskit | 2 qubits | Depth: 3 (accurate) | Superposition: 1.00 (simulated) | Entanglement: 0.75 (simulated)",
  "detected_algorithms": ["grover"],
  "algorithm_detection_source": "ml"
}
```

**Response (Classical Code):**

```json
{
  "detected_language": "python",
  "language_confidence": 0.98,
  "problem_type": "classical",
  "problem_size": 25,
  "classical_metrics": {
    "cyclomatic_complexity": 5,
    "cognitive_complexity": 8,
    "time_complexity": "O(n^2)",
    "space_complexity": "O(n)",
    "loop_count": 2,
    "conditional_count": 3,
    "function_count": 2,
    "max_nesting_depth": 3,
    "lines_of_code": 25
  },
  "quantum_metrics": null,
  "qubits_required": 0,
  "circuit_depth": 0,
  "gate_count": 0,
  "cx_gate_ratio": 0.0,
  "superposition_score": 0.0,
  "entanglement_score": 0.0,
  "time_complexity": "O(n^2)",
  "memory_requirement_mb": 8.0,
  "is_quantum": false,
  "confidence_score": 0.98,
  "analysis_notes": "Classical analysis: python | 25 LOC | Time: O(n^2) (accurate) | Space: O(n) (accurate)",
  "detected_algorithms": [],
  "algorithm_detection_source": null
}
```

---

### GET `/api/v1/code-analysis-engine/supported-languages`

List all supported programming languages.

**Response:**

```json
{
  "languages": [
    { "name": "Python", "value": "python" },
    { "name": "Qiskit", "value": "qiskit" },
    { "name": "Cirq", "value": "cirq" },
    { "name": "Qsharp", "value": "qsharp" },
    { "name": "Openqasm", "value": "openqasm" }
  ],
  "count": 5
}
```

## Supported Languages

| Language | Type      | Description                          |
| -------- | --------- | ------------------------------------ |
| Python   | Classical | Standard Python code                 |
| Qiskit   | Quantum   | IBM's quantum computing framework    |
| Cirq     | Quantum   | Google's quantum computing framework |
| Q#       | Quantum   | Microsoft's quantum language         |
| OpenQASM | Quantum   | Open Quantum Assembly Language       |

## Analysis Pipeline

The code analysis follows this pipeline:

```
Code Submission
      │
      ▼
┌─────────────────┐
│ Language        │
│ Detection       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ AST Building    │
│ (Unified AST)   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌───────┐
│Classic│ │Quantum│
│Analyze│ │Analyze│
└───┬───┘ └───┬───┘
    │         │
    │    ┌────┴────┐
    │    │         │
    │    ▼         ▼
    │ ┌─────┐ ┌─────────┐
    │ │ ML  │ │ Rule    │
    │ │Class│ │ Based   │
    │ └──┬──┘ └────┬────┘
    │    │         │
    │    └────┬────┘
    │         │
    └────┬────┘
         │
         ▼
┌─────────────────┐
│ Build Analysis  │
│ Result          │
└─────────────────┘
```

## Problem Types

The engine classifies code into the following problem types:

| Problem Type       | Description                                    |
| ------------------ | ---------------------------------------------- |
| `search`           | Search problems (e.g., Grover's algorithm)     |
| `optimization`     | Optimization problems (e.g., VQE, QAOA)        |
| `simulation`       | Quantum simulation                             |
| `machine_learning` | Quantum ML algorithms                          |
| `factorization`    | Integer factorization (e.g., Shor's algorithm) |
| `cryptography`     | Cryptographic applications                     |
| `sampling`         | Sampling problems (e.g., QFT)                  |
| `classical`        | Classical algorithms                           |

## Time Complexity Classes

| Complexity        | Notation   | Example               |
| ----------------- | ---------- | --------------------- |
| Constant          | O(1)       | Array access          |
| Logarithmic       | O(log n)   | Binary search         |
| Linear            | O(n)       | Linear search         |
| Linearithmic      | O(n log n) | Merge sort            |
| Quadratic         | O(n²)      | Bubble sort           |
| Cubic             | O(n³)      | Matrix multiplication |
| Exponential       | O(2ⁿ)      | Brute force           |
| Quantum Advantage | O(√n)      | Grover's algorithm    |

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_full_analysis.py

# Run with verbose output
pytest -v tests/
```

## Example Usage

### cURL

```bash
# Health check
curl http://localhost:8002/api/v1/code-analysis-engine/health

# Detect language
curl -X POST "http://localhost:8002/api/v1/code-analysis-engine/detect-language" \
  -H "Content-Type: application/json" \
  -d '{"code": "import cirq\nq = cirq.LineQubit.range(2)"}'

# Analyze code
curl -X POST "http://localhost:8002/api/v1/code-analysis-engine/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "from qiskit import QuantumCircuit\nqc = QuantumCircuit(3)\nqc.h(0)\nqc.cx(0, 1)\nqc.cx(1, 2)\nqc.measure_all()"
  }'
```

### Python

```python
import requests

# Analyze quantum code
code = """
from qiskit import QuantumCircuit

# Create a Grover's search circuit
qc = QuantumCircuit(2)
qc.h([0, 1])  # Superposition
qc.cz(0, 1)  # Oracle
qc.h([0, 1])  # Diffusion
qc.measure_all()
"""

response = requests.post(
    "http://localhost:8002/api/v1/code-analysis-engine/analyze",
    json={"code": code}
)

result = response.json()
print(f"Language: {result['detected_language']}")
print(f"Problem Type: {result['problem_type']}")
print(f"Qubits: {result['qubits_required']}")
print(f"Quantum Code: {result['is_quantum']}")
```

## Integration

This service integrates with:

- **Decision Engine** (port 8003): Receives analysis results for hardware recommendations
- **API Gateway**: Routes requests in microservice architecture
- **Frontend**: Provides analysis data for user interfaces

## Configuration

Environment variables can be set for configuration:

```bash
# Server
HOST=0.0.0.0
PORT=8002

# CORS Origins (configured in main.py)
# Currently allows: http://localhost:8080, http://127.0.0.1:5173
```

## Troubleshooting

### Common Issues

**Import Errors**

```bash
# Ensure all dependencies are installed
pip install -r requirements.txt
```

**Tree-sitter Build Issues**

```bash
# Rebuild tree-sitter parsers
pip uninstall tree-sitter
pip install tree-sitter==0.20.4
```

**Port Already in Use**

```bash
# Kill existing process
lsof -ti:8002 | xargs kill -9
```

**Unsupported Language Error**

- Ensure the code contains recognizable patterns for supported languages
- Check the `/supported-languages` endpoint for valid languages

### Logs

The service logs to stdout with uvicorn logger:

```bash
# View logs with timestamp
python main.py 2>&1 | while read line; do echo "$(date '+%Y-%m-%d %H:%M:%S') $line"; done
```

## Contributing

1. Follow the existing code structure
2. Add type hints to all functions
3. Update models in `models/` for schema changes
4. Add tests for new features
5. Update this README for API changes

## License

See the main project LICENSE file.
