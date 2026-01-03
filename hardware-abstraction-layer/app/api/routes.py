from fastapi import APIRouter

from app.models.quantum_models import QuantumCircuit
from app.models.classical_models import ClassicalTask
from app.models.execution import JobPriority, OptimizationStrategy, JobRequest
from app.services.factory import compute_service
from app.services.job_manager import job_manager

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
def execute_quantum_circuit(
    provider_name: str, 
    circuit: QuantumCircuit, 
    device_name: str, 
    shots: int = 1024,
    priority: JobPriority = JobPriority.HIGH,
    strategy: OptimizationStrategy = OptimizationStrategy.TIME
):
    req = JobRequest(
        task=circuit,
        provider_name=provider_name,
        device_name=device_name,
        shots=shots,
        priority=priority,
        strategy=strategy
    )
    job_id = job_manager.submit_job(req)
    return {"job_id": job_id}


@router.get("/quantum/jobs/{provider_name}/{job_id}")
def get_quantum_job_status(provider_name: str, job_id: str):
    # Try JobManager first (for HAL IDs)
    status = job_manager.get_job_status(job_id)
    if status == "UNKNOWN":
        # Fallback to direct provider check (for legacy/provider IDs)
        status = compute_service.get_job_status(provider_name, job_id)
    return {"status": status}


@router.get("/quantum/jobs/{provider_name}/{job_id}/result")
def get_quantum_job_result(provider_name: str, job_id: str):
    result = job_manager.get_job_result(job_id)
    if not result:
        result = compute_service.get_job_result(provider_name, job_id)
    return {"result": result}


@router.get("/v1/hardware/status")
def get_hardware_status():
    """
    Get the overall status of the Hardware Abstraction Layer.
    """
    providers = compute_service.list_providers()
    return {
        "status": "online",
        "service": "Hardware Abstraction Layer",
        "providers_available": len(providers),
        "providers": providers
    }


@router.get("/v1/hardware/devices")
def list_all_hardware_devices():
    """
    List all available devices from all registered providers.
    """
    all_devices = []
    providers = compute_service.list_providers()
    
    for provider in providers:
        try:
            devices = compute_service.list_devices(provider)
            # Tag devices with their provider for clarity
            for device in devices:
                device["provider"] = provider
            all_devices.extend(devices)
        except Exception as e:
            print(f"Error fetching devices for {provider}: {e}")
            
    return {"devices": all_devices}


# --- Classical Endpoints ---

@router.post("/classical/{provider_name}/execute")
def execute_classical_task(
    provider_name: str, 
    task: ClassicalTask, 
    device_name: str = "default",
    priority: JobPriority = JobPriority.HIGH,
    strategy: OptimizationStrategy = OptimizationStrategy.TIME
):
    req = JobRequest(
        task=task,
        provider_name=provider_name,
        device_name=device_name,
        priority=priority,
        strategy=strategy
    )
    job_id = job_manager.submit_job(req)
    return {"job_id": job_id}


# --- Generic Job Endpoints ---

@router.get("/jobs/{provider_name}/{job_id}")
def get_job_status(provider_name: str, job_id: str):
    status = job_manager.get_job_status(job_id)
    if status == "UNKNOWN":
        status = compute_service.get_job_status(provider_name, job_id)
    return {"status": status}


@router.get("/jobs/{provider_name}/{job_id}/result")
def get_job_result(provider_name: str, job_id: str):
    result = job_manager.get_job_result(job_id)
    if not result:
        result = compute_service.get_job_result(provider_name, job_id)
    return {"result": result}
