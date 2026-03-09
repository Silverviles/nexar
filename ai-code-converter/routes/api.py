"""API routes for the application"""
from fastapi import APIRouter, HTTPException
from models.schemas import (
    PythonCodeRequest,
    QuantumCodeRequest,
    TranslationResponse,
    ExecutionResponse,
    DeviceListResponse,
    DeviceInfo,
)
from services.ai_service import ai_service
from services.quantum_service import quantum_service
from services.hal_client import hal_client, HALError
from utils.helpers import extract_logic_function
from routes.quantum_analysis import router as quantum_analysis_router
from config.config import HAL_ENABLED

router = APIRouter(prefix="/api", tags=["quantum"])

router.include_router(quantum_analysis_router)

@router.post("/translate", response_model=TranslationResponse)
async def translate_python_to_quantum(request: PythonCodeRequest):
    """Translate Python code to quantum circuit code"""
    try:
        quantum_code = ai_service.generate_quantum_code(request.python_code)
        return TranslationResponse(
            python_code=request.python_code,
            quantum_code=quantum_code
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute", response_model=ExecutionResponse)
async def execute_quantum_code(request: QuantumCodeRequest):
    """Execute quantum circuit code and return results.

    Set ``backend`` to ``"hal"`` to run on IBM Quantum hardware via the
    Hardware Abstraction Layer.  Defaults to ``"local"`` (AerSimulator).
    """
    try:
        result = await quantum_service.safe_execute_qc(
            request.quantum_code,
            gate_type=request.gate_type,
            shots=request.shots,
            backend=request.backend,
            device_name=request.device_name,
        )
        return ExecutionResponse(**result)
    except HALError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-logic")
async def extract_logic_function_endpoint(request: PythonCodeRequest):
    """Extract minimal logic function from Python code"""
    try:
        logic_function = extract_logic_function(request.python_code)
        return {
            "original_python_code": request.python_code,
            "extracted_logic_function": logic_function
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/devices", response_model=DeviceListResponse)
async def list_hal_devices():
    """List quantum devices available through the HAL.

    Requires ``HAL_ENABLED=true`` in configuration.
    """
    if not HAL_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="HAL integration is not enabled. Set HAL_ENABLED=true.",
        )
    try:
        raw_devices = await hal_client.list_devices()
        devices = [
            DeviceInfo(
                name=d.get("name", d.get("device_name", "unknown")),
                is_simulator=d.get("is_simulator", False),
                num_qubits=d.get("num_qubits"),
                status=d.get("status"),
            )
            for d in raw_devices
        ]
        return DeviceListResponse(devices=devices)
    except HALError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    health = {"status": "healthy", "service": "quantum-code-converter"}

    if HAL_ENABLED:
        health["hal_enabled"] = True
        health["hal_reachable"] = await hal_client.health_check()

    return health
