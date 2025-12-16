from typing import List, Dict, Any

from qiskit_ibm_runtime import QiskitRuntimeService

from app.providers.base import QuantumProvider


class IBMProvider(QuantumProvider):
    """
    A quantum provider for IBM Qiskit.
    """

    def __init__(self):
        self.service = QiskitRuntimeService()

    def get_provider_name(self) -> str:
        return "ibm"

    def list_devices(self) -> List[Dict[str, Any]]:
        backends = self.service.backends()
        devices = []
        for backend in backends:
            devices.append(
                {
                    "name": backend.name,
                    "version": backend.version,
                    "description": backend.description,
                }
            )
        return devices

    def execute_circuit(self, circuit: Any, device_name: str, shots: int) -> str:
        # TODO: Implement this method
        return ""

    def get_job_status(self, job_id: str) -> str:
        # TODO: Implement this method
        return ""

    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        # TODO: Implement this method
        return {}