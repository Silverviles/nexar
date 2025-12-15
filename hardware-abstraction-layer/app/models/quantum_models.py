from typing import Dict, Any

from pydantic import BaseModel


class QuantumDevice(BaseModel):
    """
    A Pydantic model for a quantum device.
    """
    name: str
    qubits: int
    provider: str
    status: str
    other_info: Dict[str, Any] = {}


class QuantumCircuit(BaseModel):
    """
    A Pydantic model for a quantum circuit.
    """
    qasm: str


class QuantumJob(BaseModel):
    """
    A Pydantic model for a quantum job.
    """
    job_id: str
    provider: str
    status: str


class QuantumResult(BaseModel):
    """
    A Pydantic model for a quantum job result.
    """
    job_id: str
    provider: str
    result: Dict[str, Any]
