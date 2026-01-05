# AI Code Converter

A FastAPI-based microservice for converting Python code to quantum circuits and analyzing code for quantum suitability. Part of the Nexar Quantum-Classical Code Router system.

## Overview

The AI Code Converter provides intelligent code translation and analysis:

- **Code Translation**: Convert Python logic to quantum circuit implementations
- **Pattern Recognition**: Detect quantum-suitable code patterns
- **Quantum Analysis**: Evaluate code's suitability for quantum execution
- **Code Execution**: Execute generated quantum circuits and return results
- **Batch Processing**: Analyze multiple code snippets simultaneously

## Architecture

```
ai-code-converter/
├── routes/                    # API endpoints
│   ├── api.py                 # Main API routes
│   └── quantum_analysis.py    # Quantum analysis endpoints
├── services/                  # Business logic
│   ├── ai_service.py          # AI-powered code generation
│   ├── quantum_service.py     # Quantum execution service
│   ├── quantum_pattern_recognizer.py  # Pattern detection
│   └── visualization_service.py       # Result visualization
├── models/                    # Pydantic models
│   ├── schemas.py             # API request/response schemas
│   └── quantum_analysis.py    # Analysis models
├── utils/                     # Utility functions
├── config/                    # Configuration
├── AST/                       # Abstract Syntax Tree utilities
├── models.py                  # AI model definitions
├── main.py                    # FastAPI app factory
├── run.py                     # Development server runner
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Quick Start

### 1. Setup Environment

```bash
cd ai-code-converter

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
# Development mode
python run.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

The service will be available at:
- **API Root**: http://localhost:8001/
- **API Docs**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### 3. Production Deployment

```bash
# Using uvicorn with multiple workers
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4

# Using gunicorn with uvicorn workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

## API Endpoints

### Core Translation Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service info and endpoints |
| GET | `/api/health` | Health check |
| POST | `/api/translate` | Translate Python to quantum code |
| POST | `/api/execute` | Execute quantum circuit |
| POST | `/api/extract-logic` | Extract logic function |

### Quantum Analysis Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/quantum/health` | Quantum service health check |
| GET | `/api/quantum/patterns` | List detectable quantum patterns |
| POST | `/api/quantum/analyze` | Analyze code for quantum suitability |
| POST | `/api/quantum/analyze/batch` | Batch analyze multiple code snippets |
| GET | `/api/quantum/test` | Test analysis with example code |

---

## Endpoint Details

### GET `/`

Root endpoint returning service information and available endpoints.

**Response:**
```json
{
  "message": "Welcome to Python-to-Quantum API",
  "endpoints": {
    "/api/translate": "POST - Translate Python to quantum code",
    "/api/execute": "POST - Execute quantum circuit",
    "/api/extract-logic": "POST - Extract logic function",
    "/api/health": "GET - Health check",
    "/api/quantum/patterns": "GET - List detectable quantum patterns",
    "/api/quantum/analyze": "POST - Analyze code for quantum suitability",
    "/api/quantum/analyze/batch": "POST - Analyze multiple code snippets",
    "/api/quantum/test": "GET - Test analysis with example"
  }
}
```

---

### GET `/api/health`

Health check endpoint for the translation service.

**Response:**
```json
{
  "status": "healthy",
  "service": "quantum-code-converter"
}
```

---

### POST `/api/translate`

Translate Python code to quantum circuit code using AI.

**Request Body:**
```json
{
  "python_code": "def majority_vote(a, b, c):\n    return (a and b) or (b and c) or (a and c)"
}
```

**Response:**
```json
{
  "python_code": "def majority_vote(a, b, c):\n    return (a and b) or (b and c) or (a and c)",
  "quantum_code": "from qiskit import QuantumCircuit\n\nqc = QuantumCircuit(3, 1)\n\n# Encode inputs\nqc.u3(a*pi, 0, pi, 0)\nqc.u3(b*pi, 0, pi, 1)\nqc.u3(c*pi, 0, pi, 2)\n\n# Majority voting circuit\nqc.cx(0, 1)\nqc.cx(1, 2)\nqc.cx(0, 2)\n\nqc.measure(2, 0)"
}
```

---

### POST `/api/execute`

Execute quantum circuit code and return measurement results.

**Request Body:**
```json
{
  "quantum_code": "from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister\nqc = QuantumCircuit(2, 2)\nqc.h(0)\nqc.cx(0, 1)\nqc.measure([0, 1], [0, 1])",
  "gate_type": "xor",
  "shots": 1000
}
```

**Response:**
```json
{
  "success": true,
  "counts": {
    "00": 489,
    "11": 511
  },
  "probabilities": {
    "00": 0.489,
    "11": 0.511
  },
  "performance": {
    "total_gates": 4,
    "circuit_depth": 2,
    "execution_time_ms": 125.5
  },
  "images": {
    "circuit_diagram": "data:image/png;base64,...",
    "histogram": "data:image/png;base64,..."
  },
  "used_generated_code": false,
  "fallback_reason": null
}
```

---

### POST `/api/extract-logic`

Extract the minimal logic function from Python code.

**Request Body:**
```json
{
  "python_code": "import numpy as np\n\ndef compute(x):\n    return x ** 2 + 2 * x + 1\n\nresult = compute(5)\nprint(result)"
}
```

**Response:**
```json
{
  "original_python_code": "import numpy as np\n\ndef compute(x):\n    return x ** 2 + 2 * x + 1\n\nresult = compute(5)\nprint(result)",
  "extracted_logic_function": "def compute(x):\n    return x ** 2 + 2 * x + 1"
}
```

---

### GET `/api/quantum/patterns`

List all detectable quantum patterns and their mappings.

**Response:**
```json
{
  "patterns": [
    {
      "pattern": "linear_search",
      "quantum_algorithm": "Grover's Algorithm",
      "expected_speedup": 2.0,
      "base_suitability": 0.85
    },
    {
      "pattern": "optimization",
      "quantum_algorithm": "QAOA",
      "expected_speedup": 1.5,
      "base_suitability": 0.75
    },
    {
      "pattern": "majority_voting",
      "quantum_algorithm": "Deutsch-Jozsa",
      "expected_speedup": 2.0,
      "base_suitability": 0.9
    }
  ],
  "count": 3
}
```

---

### POST `/api/quantum/analyze`

Analyze Python code for quantum suitability and detect quantum patterns.

**Request Body:**
```json
{
  "code": "def search_list(lst, target):\n    for i in range(len(lst)):\n        if lst[i] == target:\n            return i\n    return -1",
  "include_code": false
}
```

**Response:**
```json
{
  "success": true,
  "patterns": [
    {
      "pattern": "linear_search",
      "confidence": 0.92,
      "quantum_algo": "Grover's Algorithm",
      "speedup": 2.0,
      "suitability_score": 0.85
    }
  ],
  "quantum_suitability": {
    "score": 0.85,
    "level": "HIGH",
    "message": "Code exhibits patterns suitable for quantum acceleration"
  },
  "metrics": {
    "lines_of_code": 5,
    "cyclomatic_complexity": 2,
    "loop_count": 1,
    "conditional_count": 1,
    "function_count": 1
  }
}
```

**Query Parameters:**
- `include_code` (boolean, default: false) - Include original code in response

**Note:** Original code is automatically included if suitability level is HIGH.

---

### POST `/api/quantum/analyze/batch`

Analyze multiple code snippets in a single batch request.

**Request Body:**
```json
{
  "codes": [
    {
      "id": "snippet_1",
      "code": "def search(lst, target):\n    for i in range(len(lst)):\n        if lst[i] == target:\n            return i\n    return -1"
    },
    {
      "id": "snippet_2",
      "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "id": "snippet_1",
      "success": true,
      "patterns": [
        {
          "pattern": "linear_search",
          "confidence": 0.92,
          "quantum_algo": "Grover's Algorithm",
          "speedup": 2.0,
          "suitability_score": 0.85
        }
      ],
      "quantum_suitability": {
        "score": 0.85,
        "level": "HIGH",
        "message": "Code exhibits patterns suitable for quantum acceleration"
      },
      "metrics": {
        "lines_of_code": 5,
        "cyclomatic_complexity": 2,
        "loop_count": 1,
        "conditional_count": 1,
        "function_count": 1
      }
    },
    {
      "id": "snippet_2",
      "success": true,
      "patterns": [],
      "quantum_suitability": {
        "score": 0.15,
        "level": "LOW",
        "message": "Code does not exhibit quantum advantage patterns"
      },
      "metrics": {
        "lines_of_code": 5,
        "cyclomatic_complexity": 2,
        "loop_count": 0,
        "conditional_count": 1,
        "function_count": 1
      }
    }
  ],
  "processed": 2,
  "successful": 2
}
```

---

### GET `/api/quantum/test`

Test the quantum analysis service with example code.

**Response:**
```json
{
  "example_code": "def majority_voting(a, b, c):\n    return (a and b) or (b and c) or (a and c)",
  "analysis": {
    "success": true,
    "patterns": [
      {
        "pattern": "majority_voting",
        "confidence": 0.88,
        "quantum_algo": "Deutsch-Jozsa Algorithm",
        "speedup": 2.0,
        "suitability_score": 0.9
      }
    ],
    "quantum_suitability": {
      "score": 0.9,
      "level": "HIGH",
      "message": "Strong quantum advantage detected"
    },
    "metrics": {
      "lines_of_code": 2,
      "cyclomatic_complexity": 1,
      "loop_count": 0,
      "conditional_count": 0,
      "function_count": 1
    }
  }
}
```

---

## Detectable Quantum Patterns

| Pattern | Quantum Algorithm | Speedup | Suitability |
|---------|------------------|---------|-------------|
| Linear Search | Grover's Algorithm | 2x | High |
| Optimization | QAOA | 1.5x | Medium |
| Majority Voting | Deutsch-Jozsa | 2x | High |
| Factorization | Shor's Algorithm | Exponential | High |
| Database Search | Amplitude Amplification | 2x | High |

## Quantum Suitability Levels

| Level | Score Range | Description |
|-------|-------------|-------------|
| HIGH | 0.75 - 1.0 | Strong quantum advantage potential |
| MEDIUM | 0.5 - 0.74 | Moderate quantum advantage |
| LOW | 0.0 - 0.49 | Limited quantum advantage |

## Request Models

### PythonCodeRequest
```json
{
  "python_code": "string - Python source code"
}
```

### QuantumCodeRequest
```json
{
  "quantum_code": "string - Quantum circuit code",
  "gate_type": "string - Gate type (default: 'xor')",
  "shots": "integer - Number of measurement shots (default: 1000)"
}
```

### AnalysisRequest
```json
{
  "code": "string - Python source code to analyze",
  "include_code": "boolean - Include original code in response (default: false)"
}
```

### BatchAnalysisRequest
```json
{
  "codes": [
    {
      "id": "string - Unique identifier",
      "code": "string - Python source code"
    }
  ]
}
```

## Code Metrics

The analysis returns the following code metrics:

- **lines_of_code** - Total lines of source code
- **cyclomatic_complexity** - McCabe complexity score
- **loop_count** - Number of loops detected
- **conditional_count** - Number of if/else statements
- **function_count** - Number of functions defined

## Error Handling

All endpoints return appropriate HTTP status codes and error messages:

```json
{
  "detail": "Error description"
}
```

**Common Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid code or parameters)
- `500` - Internal Server Error

## Example Usage

### cURL

```bash
# Health check
curl http://localhost:8001/api/health

# Analyze code for quantum suitability
curl -X POST "http://localhost:8001/api/quantum/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def search(lst, target):\n    for i in range(len(lst)):\n        if lst[i] == target:\n            return i\n    return -1"
  }'

# Translate Python to quantum
curl -X POST "http://localhost:8001/api/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "python_code": "def majority(a, b, c):\n    return (a and b) or (b and c) or (a and c)"
  }'
```

### Python

```python
import requests

# Analyze code
code = """
def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1
"""

response = requests.post(
    "http://localhost:8001/api/quantum/analyze",
    json={"code": code}
)

result = response.json()
print(f"Quantum Suitability: {result['quantum_suitability']['level']}")
print(f"Score: {result['quantum_suitability']['score']}")
print(f"Patterns Detected: {[p['pattern'] for p in result['patterns']]}")
```

### JavaScript/Fetch

```javascript
// Analyze code
const code = `
def majority_vote(a, b, c):
    return (a and b) or (b and c) or (a and c)
`;

fetch('http://localhost:8001/api/quantum/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ code })
})
.then(res => res.json())
.then(data => {
  console.log('Suitability:', data.quantum_suitability.level);
  console.log('Score:', data.quantum_suitability.score);
})
.catch(err => console.error(err));
```

## Integration

This service integrates with:

- **Code Analysis Engine** (port 8002): Complements with detailed complexity analysis
- **Decision Engine** (port 8083): Receives suitability analysis for routing
- **Frontend**: Provides conversion and analysis UI
- **API Gateway**: Routes requests in microservice architecture

## Development

### Project Structure

- **routes/**: API endpoint definitions
- **services/**: Business logic and ML services
- **models/**: Pydantic schemas and data models
- **utils/**: Helper functions
- **config/**: Configuration management

### Adding New Patterns

1. Update `QUANTUM_MAPPINGS` in `quantum_pattern_recognizer.py`
2. Add pattern detection logic
3. Test with `/api/quantum/test` endpoint

## Dependencies

Key dependencies:
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **pydantic** - Data validation
- **qiskit** - Quantum computing framework
- **torch/transformers** - ML for code generation
- **scikit-learn** - ML utilities

## Contributing

1. Follow the existing code structure
2. Add type hints to all functions
3. Update schemas for API changes
4. Test endpoints using `/docs` interface
5. Update this README for new features

## Troubleshooting

### Common Issues

**Dependencies Installation**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Port Already in Use**
```bash
# Change port in run.py or use:
uvicorn main:app --port 8001
```

**Model Loading Issues**
```bash
# Ensure all dependencies are installed
pip install torch transformers
```

## License

See the main project LICENSE file.
