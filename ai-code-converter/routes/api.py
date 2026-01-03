"""API routes for the application"""
from fastapi import APIRouter, HTTPException
from models.schemas import (
    PythonCodeRequest,
    QuantumCodeRequest,
    TranslationResponse,
    ExecutionResponse,
)
from services.ai_service import ai_service
from services.quantum_service import quantum_service
from utils.helpers import extract_logic_function

router = APIRouter(prefix="/api", tags=["quantum"])

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
    """Execute quantum circuit code and return results"""
    try:
        result = quantum_service.safe_execute_qc(
            request.quantum_code,
            gate_type=request.gate_type,
            shots=request.shots
        )
        return ExecutionResponse(**result)
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

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "quantum-code-converter"}