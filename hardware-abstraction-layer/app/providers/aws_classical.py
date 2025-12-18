import uuid
from typing import List, Dict, Any

from app.models.classical_models import ClassicalTask
from app.providers.base import ClassicalProvider


class AWSClassicalProvider(ClassicalProvider):
    """
    A classical provider for AWS (e.g., Lambda, EC2, Fargate).
    """

    def get_provider_name(self) -> str:
        return "aws-classical"

    def list_devices(self) -> List[Dict[str, Any]]:
        # Mocking AWS execution environments
        return [
            {
                "name": "aws_lambda",
                "type": "serverless",
                "description": "AWS Lambda",
                "status": "active"
            },
            {
                "name": "aws_fargate",
                "type": "container",
                "description": "AWS Fargate",
                "status": "active"
            }
        ]

    def execute_task(self, task: ClassicalTask, device_name: str = "default") -> str:
        # Mock execution
        return str(uuid.uuid4())

    def get_job_status(self, job_id: str) -> str:
        return "COMPLETED"

    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        return {"message": "Executed on AWS (Mock)"}
