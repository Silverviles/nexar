from fastapi import APIRouter

from app.models.classical_models import ClassicalTask
from app.models.quantum_models import QuantumCircuit
from app.services.factory import compute_service

router = APIRouter(prefix="/api")


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/providers")
def list_providers():
    return {"providers": compute_service.list_providers()}


@router.get("/quantum/{provider_name}/devices")
def list_quantum_devices(provider_name: str):
    return {"devices": compute_service.list_devices(provider_name)}


@router.post("/quantum/{provider_name}/execute")
def execute_quantum_circuit(provider_name: str, circuit: QuantumCircuit, device_name: str, shots: int = 1024):
    # TODO: Validate that circuit is converted to the correct format for the provider if needed
    job_id = compute_service.execute_quantum_circuit(provider_name, circuit, device_name, shots)
    return {"job_id": job_id}


@router.get("/quantum/jobs/{provider_name}/{job_id}")
def get_quantum_job_status(provider_name: str, job_id: str):
    status = compute_service.get_job_status(provider_name, job_id)
    return {"status": status}


@router.get("/quantum/jobs/{provider_name}/{job_id}/result")
def get_quantum_job_result(provider_name: str, job_id: str):
    result = compute_service.get_job_result(provider_name, job_id)
    return {"result": result}


# --- Classical Endpoints ---

@router.post("/classical/{provider_name}/execute")
def execute_classical_task(provider_name: str, task: ClassicalTask, device_name: str = "default"):
    job_id = compute_service.execute_classical_task(provider_name, task, device_name)
    return {"job_id": job_id}


# --- Generic Job Endpoints ---

@router.get("/jobs/{provider_name}/{job_id}")
def get_job_status(provider_name: str, job_id: str):
    status = compute_service.get_job_status(provider_name, job_id)
    return {"status": status}


@router.get("/jobs/{provider_name}/{job_id}/result")
def get_job_result(provider_name: str, job_id: str):
    result = compute_service.get_job_result(provider_name, job_id)
    return {"result": result}
