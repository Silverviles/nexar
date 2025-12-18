from typing import List, Dict, Any

from app.models.classical_models import ClassicalTask
from app.providers.base import BaseProvider, QuantumProvider, ClassicalProvider


class ComputeService:
    """
    A service for interacting with compute providers (Quantum and Classical).
    """

    def __init__(self):
        self._providers: Dict[str, BaseProvider] = {}

    def register_provider(self, provider: BaseProvider):
        """
        Registers a provider.
        """
        provider_name = provider.get_provider_name()
        self._providers[provider_name] = provider

    def list_providers(self) -> List[str]:
        """
        Lists the registered providers.
        """
        return list(self._providers.keys())

    def list_devices(self, provider_name: str) -> List[Dict[str, Any]]:
        """
        Lists the available devices for a provider.
        """
        provider = self._get_provider(provider_name)
        return provider.list_devices()

    def execute_quantum_circuit(self, provider_name: str, circuit: Any, device_name: str, shots: int) -> str:
        """
        Executes a quantum circuit.
        """
        provider = self._get_provider(provider_name)
        if not isinstance(provider, QuantumProvider):
            raise ValueError(f"Provider '{provider_name}' is not a QuantumProvider.")
        return provider.execute_circuit(circuit, device_name, shots)

    def execute_classical_task(self, provider_name: str, task: ClassicalTask, device_name: str = "default") -> str:
        """
        Executes a classical task.
        """
        provider = self._get_provider(provider_name)
        if not isinstance(provider, ClassicalProvider):
            raise ValueError(f"Provider '{provider_name}' is not a ClassicalProvider.")
        return provider.execute_task(task, device_name)

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

    def _get_provider(self, provider_name: str) -> BaseProvider:
        """
        Gets a provider by name.
        """
        if provider_name not in self._providers:
            raise ValueError(f"Provider '{provider_name}' not registered.")
        return self._providers[provider_name]
