from typing import Dict, Any, Optional
from pydantic import BaseModel

class PythonCodeRequest(BaseModel):
    python_code: str

class QuantumCodeRequest(BaseModel):
    quantum_code: str
    gate_type: str = "xor"
    shots: int = 1000

class TranslationResponse(BaseModel):
    python_code: str
    quantum_code: str

class ExecutionResponse(BaseModel):
    success: bool
    counts: Dict[str, int]
    probabilities: Dict[str, float]
    performance: Dict[str, Any]
    images: Dict[str, str]
    used_generated_code: bool
    fallback_reason: Optional[str] = None

class ErrorResponse(BaseModel):
    detail: str