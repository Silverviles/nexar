import uuid
from typing import List, Dict, Any

from app.models.classical_models import ClassicalTask
from app.providers.base import ClassicalProvider


class CPUClassicalProvider(ClassicalProvider):
    """
    Classical provider for CPU-based compute.

    Placeholder for dedicated CPU execution backends (e.g., bare-metal
    servers, high-core-count instances).  Currently returns mock results;
    swap in a real executor when a CPU cluster is provisioned.
    """

    def get_provider_name(self) -> str:
        return "cpu-classical"

    def list_devices(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "cpu_general",
                "type": "cpu",
                "description": "General-purpose CPU compute node",
                "status": "available",
                "specs": {
                    "architecture": "x86_64",
                    "cores": 64,
                    "clock_ghz": 3.5,
                    "memory_gb": 256,
                    "provider": "cpu-classical",
                },
            }
        ]

    def execute_task(self, task: ClassicalTask, device_name: str = "default") -> str:
        # TODO: route to a real CPU execution backend
        return str(uuid.uuid4())

    def get_job_status(self, job_id: str) -> str:
        return "COMPLETED"

    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        return {"message": "Executed on CPU backend (placeholder)"}
