from fastapi import APIRouter
from app.services.factory import quantum_service
from app.models.quantum_models import QuantumCircuit
from typing import Any

router = APIRouter(prefix="/api")

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/quantum/{provider_name}/devices")
def list_quantum_devices(provider_name: str):
    return {"devices": quantum_service.list_devices(provider_name)}

@router.post("/quantum/{provider_name}/execute")
def execute_quantum_circuit(provider_name: str, circuit: QuantumCircuit, device_name: str, shots: int = 1024):
    job_id = quantum_service.execute_circuit(provider_name, circuit, device_name, shots)
    return {"job_id": job_id}

@router.get("/quantum/jobs/{provider_name}/{job_id}")
def get_quantum_job_status(provider_name: str, job_id: str):
    status = quantum_service.get_job_status(provider_name, job_id)
    return {"status": status}

@router.get("/quantum/jobs/{provider_name}/{job_id}/result")
def get_quantum_job_result(provider_name: str, job_id: str):
    result = quantum_service.get_job_result(provider_name, job_id)
    return {"result": result}
