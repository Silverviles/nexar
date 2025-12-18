import uuid
from typing import List, Dict, Any

from app.models.classical_models import ClassicalTask
from app.providers.base import ClassicalProvider


class IBMClassicalProvider(ClassicalProvider):
    """
    A classical provider for IBM Cloud (e.g., IBM Cloud Functions or Code Engine).
    """

    def get_provider_name(self) -> str:
        return "ibm-classical"

    def list_devices(self) -> List[Dict[str, Any]]:
        # Mocking IBM Cloud execution environments
        return [
            {
                "name": "ibm_cloud_functions",
                "type": "serverless",
                "description": "IBM Cloud Functions (Apache OpenWhisk)",
                "status": "active"
            },
            {
                "name": "ibm_code_engine",
                "type": "container",
                "description": "IBM Cloud Code Engine",
                "status": "active"
            }
        ]

    def execute_task(self, task: ClassicalTask, device_name: str = "default") -> str:
        # Mock execution
        return str(uuid.uuid4())

    def get_job_status(self, job_id: str) -> str:
        return "COMPLETED"

    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        return {"message": "Executed on IBM Cloud (Mock)"}
