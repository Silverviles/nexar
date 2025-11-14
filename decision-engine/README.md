# Decision Engine API

A FastAPI-based microservice for making intelligent hardware recommendations in the Quantum-Classical Code Router system. This service analyzes code characteristics and recommends whether to execute on quantum or classical hardware using machine learning models.

## Overview

The Decision Engine receives code analysis results from the Code Analysis Engine and uses trained ML models to predict optimal hardware execution based on factors like:

- Problem type and complexity
- Quantum circuit characteristics (qubits, gates, depth)
- Superposition and entanglement potential
- Memory requirements
- Time complexity

## Architecture

```
decision-engine/
├── config/                 # Configuration management
│   ├── __init__.py
│   └── app_config.py      # Pydantic settings
├── models/                # Database models (SQLAlchemy)
│   ├── __init__.py
│   └── decision_engine.py
├── routes/                # FastAPI route handlers
│   ├── __init__.py
│   └── decision_engine_routes.py
├── schemas/               # Pydantic request/response schemas
│   ├── __init__.py
│   └── decision_engine.py
├── services/              # Business logic layer
│   ├── __init__.py
│   └── decision_engine_service.py
├── ml_models/             # Trained ML models and scalers
│   ├── decision_engine_model.pkl
│   ├── feature_scaler.pkl
│   └── README.md
├── scripts/               # Setup and run scripts
│   ├── setup.py          # Environment setup
│   └── run.py            # Development server runner
├── main.py               # FastAPI application entry point
├── requirements.txt      # Python dependencies
├── example.env          # Environment variables template
├── .env                 # Environment variables (created from example.env)
└── README.md           # This file
```

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Quick Start

### 1. Setup Environment

The management script automatically detects and activates virtual environments (`.venv` or `venv`).

```bash
cd decision-engine

# Option 1: Create virtual environment and setup (recommended)
./manage.sh venv     # Create virtual environment
./manage.sh setup    # Setup everything (auto-activates venv)

# Option 2: Use existing virtual environment
source .venv/bin/activate  # Manual activation
./manage.sh setup          # Setup will detect activated venv

# Option 3: Run setup directly
python scripts/setup.py
```

This will:
- Install all Python dependencies from `requirements.txt`
- Copy `example.env` to `.env` for configuration
- Create mock ML models if none exist
- Verify project structure

### 2. Configuration

The service uses environment variables defined in `.env`. Key settings:

```properties
# Server Configuration
HOST=0.0.0.0           # Server host (0.0.0.0 for all interfaces)
PORT=8083              # Server port
DEBUG=False            # Enable debug mode for development

# ML Models
MODEL_PATH=ml_models/decision_engine_model.pkl    # Path to trained model
SCALER_PATH=ml_models/feature_scaler.pkl          # Path to feature scaler

# Database
DATABASE_URL=sqlite:///./decision_engine.db       # SQLite database URL

# CORS (for frontend integration)
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Logging
LOG_LEVEL=INFO         # Logging level (DEBUG, INFO, WARNING, ERROR)
```

### 3. Run the Service

Start the development server:

```bash
# Option 1: Use the management script (recommended)
./manage.sh run

# Option 2: Run directly  
python scripts/run.py

# Option 3: Development mode with debug logging
./manage.sh dev
```

The service will be available at:
- **API Docs**: http://localhost:8083/docs
- **ReDoc**: http://localhost:8083/redoc  
- **Health Check**: http://localhost:8083/api/v1/decision-engine/health

### 4. Production Deployment

For production, run with a WSGI server:

```bash
# Using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8083 --workers 4

# Using gunicorn with uvicorn workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8083
```

## API Endpoints

### Core Endpoints

- **POST** `/api/v1/decision-engine/predict` - Hardware recommendation
- **GET** `/api/v1/decision-engine/health` - Service health check  
- **GET** `/api/v1/decision-engine/model-info` - ML model information

### Example Request

```bash
curl -X POST "http://localhost:8083/api/v1/decision-engine/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_type": "optimization",
    "problem_size": 500,
    "qubits_required": 12,
    "circuit_depth": 150,
    "gate_count": 500,
    "cx_gate_ratio": 0.33,
    "superposition_score": 0.75,
    "entanglement_score": 0.70,
    "time_complexity": "polynomial_speedup",
    "memory_requirement_mb": 200.0
  }'
```

### Example Response

```json
{
  "success": true,
  "recommendation": {
    "recommended_hardware": "Quantum",
    "confidence": 0.87,
    "quantum_probability": 0.87,
    "classical_probability": 0.13,
    "rationale": "Problem exhibits strong quantum advantage with high superposition and entanglement scores"
  },
  "alternatives": [
    {
      "hardware": "Classical",
      "confidence": 0.13,
      "trade_off": "Lower cost but slower execution"
    }
  ],
  "estimated_execution_time_ms": 1500.0,
  "estimated_cost_usd": 0.25
}
```

## Management Scripts

The `manage.sh` script provides convenient shortcuts for common tasks and automatically handles virtual environment activation:

```bash
# Create virtual environment
./manage.sh venv

# Setup environment (detects and uses virtual environment)
./manage.sh setup

# Run the service (auto-activates venv if available)
./manage.sh run

# Run in development mode  
./manage.sh dev

# Install dependencies only
./manage.sh install

# Test the service
./manage.sh test

# Clean temporary files
./manage.sh clean
```

**Virtual Environment Support:**
- The scripts automatically detect and use `.venv/` or `venv/` directories
- No need to manually activate virtual environments when using `manage.sh`
- Creates isolated Python environments for better dependency management

## Development

### Project Structure

- **config/**: Application configuration using Pydantic Settings
- **models/**: SQLAlchemy database models for logging decisions
- **routes/**: FastAPI route handlers and API endpoints
- **schemas/**: Pydantic models for request/response validation
- **services/**: Business logic and ML model integration
- **scripts/**: Development and deployment utilities

### Adding New Features

1. **New API Endpoint**: Add routes in `routes/decision_engine_routes.py`
2. **Request/Response Schema**: Define in `schemas/decision_engine.py`
3. **Business Logic**: Implement in `services/decision_engine_service.py`
4. **Database Models**: Add to `models/decision_engine.py`

### Testing

```bash
# Run the test HTTP file
# Edit test_main.http with your test cases

# Check service health
curl http://localhost:8083/api/v1/decision-engine/health

# Validate API with built-in docs
open http://localhost:8083/docs
```

## Machine Learning Models

The service expects trained ML models in the `ml_models/` directory:

- `decision_engine_model.pkl`: Trained classifier (scikit-learn/XGBoost)
- `feature_scaler.pkl`: Feature preprocessing scaler
- `model_info.json`: Model metadata (optional)

### Model Requirements

The models should expect features in this order:
1. problem_size
2. qubits_required  
3. circuit_depth
4. gate_count
5. cx_gate_ratio
6. superposition_score
7. entanglement_score
8. memory_requirement_mb
9. problem_type_encoded (integer)
10. time_complexity_encoded (integer)

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt
```

**Model Not Found**
```bash
# Check if models exist
ls ml_models/
# Run setup to create mock models
python scripts/setup.py
```

**Port Already in Use**
```bash
# Change PORT in .env file or kill existing process
lsof -ti:8083 | xargs kill -9
```

**CORS Issues**
```bash
# Add your frontend URL to CORS_ORIGINS in .env
CORS_ORIGINS=["http://localhost:3000", "your-frontend-url"]
```

### Logs

The service logs to stdout. For production, configure proper logging:

```bash
# View logs in real-time
python scripts/run.py | tee decision-engine.log

# Set debug logging in .env
DEBUG=True
LOG_LEVEL=DEBUG
```

## Integration

This service integrates with:

- **Code Analysis Engine**: Receives analysis results
- **Hardware Abstraction Layer**: Sends execution recommendations  
- **Frontend**: Provides API for user interfaces
- **API Gateway**: Routes requests in microservice architecture

## Contributing

1. Follow the existing code structure
2. Add type hints to all functions
3. Update schemas for API changes
4. Test endpoints using the FastAPI docs interface
5. Update this README for new features

## License

See the main project LICENSE file.