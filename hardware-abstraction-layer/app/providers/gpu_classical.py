import uuid
from typing import List, Dict, Any

from app.models.classical_models import ClassicalTask
from app.providers.base import ClassicalProvider


class GPUClassicalProvider(ClassicalProvider):
    """
    Classical provider for GPU-accelerated compute.

    Placeholder for GPU execution backends (e.g., NVIDIA A100/H100
    instances for CUDA workloads).  Currently returns mock results;
    swap in a real executor when a GPU cluster is provisioned.
    """

    def get_provider_name(self) -> str:
        return "gpu-classical"

    def list_devices(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "gpu_accelerator",
                "type": "gpu",
                "description": "GPU-accelerated compute node",
                "status": "available",
                "specs": {
                    "architecture": "NVIDIA H100",
                    "vram_gb": 80,
                    "cuda_cores": 16896,
                    "tensor_cores": 528,
                    "memory_gb": 512,
                    "provider": "gpu-classical",
                },
            }
        ]

    def execute_task(self, task: ClassicalTask, device_name: str = "default") -> str:
        # TODO: route to a real GPU execution backend (e.g., CUDA runner)
        return str(uuid.uuid4())

    def get_job_status(self, job_id: str) -> str:
        return "COMPLETED"

    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        return {"message": "Executed on GPU backend (placeholder)"}
