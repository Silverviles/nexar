from typing import Dict, Any, List, Optional
from pydantic import BaseModel, field_validator


class PythonCodeRequest(BaseModel):
    python_code: str


class QuantumCodeRequest(BaseModel):
    quantum_code: str
    gate_type: str = "xor"
    shots: int = 1000
    backend: str = "local"
    device_name: Optional[str] = None

    @field_validator("backend")
    @classmethod
    def _validate_backend(cls, v: str) -> str:
        if v not in ("local", "hal"):
            raise ValueError("backend must be 'local' or 'hal'")
        return v


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
    backend_used: str = "local"
    device_name: Optional[str] = None


class DeviceInfo(BaseModel):
    name: str
    is_simulator: bool = False
    num_qubits: Optional[int] = None
    status: Optional[str] = None


class DeviceListResponse(BaseModel):
    devices: List[DeviceInfo]
    provider: str = "ibm-quantum"


class ErrorResponse(BaseModel):
    detail: str