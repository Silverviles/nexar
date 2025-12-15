from typing import List, Dict, Any

from app.providers.base import QuantumProvider


class AWSProvider(QuantumProvider):
    """
    A quantum provider for AWS Braket.
    """

    def get_provider_name(self) -> str:
        return "aws"

    def list_devices(self) -> List[Dict[str, Any]]:
        # TODO: Implement this method
        return []

    def execute_circuit(self, circuit: Any, device_name: str, shots: int) -> str:
        # TODO: Implement this method
        return ""

    def get_job_status(self, job_id: str) -> str:
        # TODO: Implement this method
        return ""

    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        # TODO: Implement this method
        return {}
