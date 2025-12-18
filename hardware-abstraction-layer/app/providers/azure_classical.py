import uuid
from typing import List, Dict, Any

from app.models.classical_models import ClassicalTask
from app.providers.base import ClassicalProvider


class AzureClassicalProvider(ClassicalProvider):
    """
    A classical provider for Azure (e.g., Azure Functions, Container Instances).
    """

    def get_provider_name(self) -> str:
        return "azure-classical"

    def list_devices(self) -> List[Dict[str, Any]]:
        # Mocking Azure execution environments
        return [
            {
                "name": "azure_functions",
                "type": "serverless",
                "description": "Azure Functions",
                "status": "active"
            },
            {
                "name": "azure_container_instances",
                "type": "container",
                "description": "Azure Container Instances",
                "status": "active"
            }
        ]

    def execute_task(self, task: ClassicalTask, device_name: str = "default") -> str:
        # Mock execution
        return str(uuid.uuid4())

    def get_job_status(self, job_id: str) -> str:
        return "COMPLETED"

    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        return {"message": "Executed on Azure (Mock)"}
