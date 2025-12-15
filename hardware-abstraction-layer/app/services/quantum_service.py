from typing import List, Dict, Any

from app.providers.base import QuantumProvider


class QuantumService:
    """
    A service for interacting with quantum providers.
    """

    def __init__(self):
        self._providers: Dict[str, QuantumProvider] = {}

    def register_provider(self, provider: QuantumProvider):
        """
        Registers a quantum provider.
        """
        provider_name = provider.get_provider_name()
        self._providers[provider_name] = provider

    def list_providers(self) -> List[str]:
        """
        Lists the registered quantum providers.
        """
        return list(self._providers.keys())

    def list_devices(self, provider_name: str) -> List[Dict[str, Any]]:
        """
        Lists the available quantum devices for a provider.
        """
        provider = self._get_provider(provider_name)
        return provider.list_devices()

    def execute_circuit(self, provider_name: str, circuit: Any, device_name: str, shots: int) -> str:
        """
        Executes a quantum circuit on a specified device.
        """
        provider = self._get_provider(provider_name)
        return provider.execute_circuit(circuit, device_name, shots)

    def get_job_status(self, provider_name: str, job_id: str) -> str:
        """
        Gets the status of a job.
        """
        provider = self._get_provider(provider_name)
        return provider.get_job_status(job_id)

    def get_job_result(self, provider_name: str, job_id: str) -> Dict[str, Any]:
        """
        Gets the result of a job.
        """
        provider = self._get_provider(provider_name)
        return provider.get_job_result(job_id)

    def _get_provider(self, provider_name: str) -> QuantumProvider:
        """
        Gets a provider by name.
        """
        if provider_name not in self._providers:
            raise ValueError(f"Provider '{provider_name}' not registered.")
        return self._providers[provider_name]
