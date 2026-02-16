from typing import List, Dict, Any

from app.models.classical_models import ClassicalTask
from app.models.execution import DeviceAvailability
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

    def execute_batch(self, provider_name: str, tasks: List[Any], device_name: str, **kwargs) -> List[str]:
        """
        Executes a batch of tasks.
        """
        provider = self._get_provider(provider_name)
        return provider.execute_batch(tasks, device_name, **kwargs)

    def execute_python_code(self, provider_name: str, code: str, device_name: str, shots: int = 1024) -> str:
        """
        Executes user-submitted Python code on a quantum provider.

        The code must define a 'circuit' variable that is a QuantumCircuit.
        Currently only supported by IBM Quantum provider.

        Args:
            provider_name: Name of the quantum provider (e.g., "ibm-quantum")
            code: Python code string
            device_name: Backend device name
            shots: Number of measurement shots

        Returns:
            job_id: The provider job ID
        """
        provider = self._get_provider(provider_name)
        if not isinstance(provider, QuantumProvider):
            raise ValueError(f"Provider '{provider_name}' is not a QuantumProvider.")

        # Check if provider supports Python code execution
        if not hasattr(provider, 'execute_python_code'):
            raise ValueError(f"Provider '{provider_name}' does not support Python code execution.")

        return provider.execute_python_code(code, device_name, shots)

    def check_device_availability(self, provider_name: str, device_name: str) -> DeviceAvailability:
        """
        Check if a specific device is available for job submission.

        Args:
            provider_name: Name of the provider
            device_name: Name of the device/backend

        Returns:
            DeviceAvailability with operational status and queue info
        """
        provider = self._get_provider(provider_name)

        # Check if provider supports availability checking
        if not hasattr(provider, 'check_device_availability'):
            # Return a default availability for providers that don't support this
            from app.core.config import settings
            return DeviceAvailability(
                device_name=device_name,
                is_operational=True,
                pending_jobs=0,
                queue_threshold=settings.DEVICE_QUEUE_THRESHOLD
            )

        return provider.check_device_availability(device_name)

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
