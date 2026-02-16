from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException

from app.models.quantum_models import QuantumCircuit
from app.models.classical_models import ClassicalTask
from app.models.execution import (
    JobPriority, OptimizationStrategy, JobRequest,
    PythonCodeRequest, DeviceAvailability
)
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


# --- IBM Quantum Specific Endpoints ---

@router.post("/quantum/ibm-quantum/execute-python")
def execute_python_code(request: PythonCodeRequest):
    """
    Execute user-submitted Python code on IBM Quantum.

    The code must define a 'circuit' variable that is a QuantumCircuit.

    Pre-loaded namespace includes:
    - QuantumCircuit, QuantumRegister, ClassicalRegister, Parameter (from qiskit)
    - numpy/np
    - math, pi, sqrt, sin, cos, exp

    Example code:
    ```python
    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure([0, 1], [0, 1])
    ```
    """
    try:
        job_id = job_manager.submit_python_code_job(
            code=request.code,
            device_name=request.device_name,
            shots=request.shots,
            scheduled_time=request.scheduled_time,
            queue_if_unavailable=request.queue_if_unavailable
        )

        response = {"job_id": job_id}
        if request.scheduled_time:
            response["scheduled_for"] = request.scheduled_time.isoformat()
        if request.queue_if_unavailable:
            # Check if job was queued due to unavailability
            status = job_manager.get_job_status(job_id)
            if status == "QUEUED_UNAVAILABLE":
                response["queued_reason"] = "Device unavailable - job queued for later execution"

        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/quantum/ibm-quantum/schedule")
def schedule_quantum_job(
    device_name: str,
    scheduled_time: datetime,
    circuit: Optional[QuantumCircuit] = None,
    code: Optional[str] = None,
    shots: int = 1024,
    queue_if_unavailable: bool = False
):
    """
    Schedule a quantum job for future execution.

    Provide either:
    - circuit: A QuantumCircuit object (QASM)
    - code: Python code that defines a 'circuit' variable

    The job will be held until the scheduled_time is reached, then executed.
    """
    if not circuit and not code:
        raise HTTPException(
            status_code=400,
            detail="Must provide either 'circuit' (QASM) or 'code' (Python)"
        )

    if circuit and code:
        raise HTTPException(
            status_code=400,
            detail="Provide only one of 'circuit' or 'code', not both"
        )

    if scheduled_time <= datetime.now():
        raise HTTPException(
            status_code=400,
            detail="scheduled_time must be in the future"
        )

    try:
        if code:
            # Python code job
            job_id = job_manager.submit_python_code_job(
                code=code,
                device_name=device_name,
                shots=shots,
                scheduled_time=scheduled_time,
                queue_if_unavailable=queue_if_unavailable
            )
        else:
            # QASM circuit job
            req = JobRequest(
                task=circuit,
                provider_name="ibm-quantum",
                device_name=device_name,
                shots=shots,
                priority=JobPriority.HIGH
            )
            job_id = job_manager.submit_job(
                req,
                scheduled_time=scheduled_time,
                queue_if_unavailable=queue_if_unavailable
            )

        return {
            "job_id": job_id,
            "status": "SCHEDULED",
            "scheduled_for": scheduled_time.isoformat(),
            "device": device_name
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/quantum/ibm-quantum/scheduled-jobs")
def list_scheduled_jobs():
    """
    List all scheduled jobs waiting for execution.
    """
    jobs = job_manager.get_scheduled_jobs()
    return {"scheduled_jobs": jobs, "count": len(jobs)}


@router.delete("/quantum/ibm-quantum/scheduled-jobs/{job_id}")
def cancel_scheduled_job(job_id: str):
    """
    Cancel a scheduled job before it executes.
    """
    success = job_manager.cancel_scheduled_job(job_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Scheduled job '{job_id}' not found"
        )
    return {"job_id": job_id, "status": "CANCELLED"}


@router.get("/quantum/ibm-quantum/devices/{device_name}/availability")
def check_device_availability(device_name: str) -> DeviceAvailability:
    """
    Check if a specific IBM Quantum device is available for job submission.

    Returns:
    - is_operational: Device is online and accepting jobs
    - pending_jobs: Number of jobs in queue
    - queue_threshold: Configured threshold for availability
    - is_available: True if operational AND pending_jobs < threshold
    """
    return compute_service.check_device_availability("ibm-quantum", device_name)


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
