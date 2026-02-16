from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseProvider(ABC):
    """
    An abstract base class for all compute providers (Quantum and Classical).
    """

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Returns the name of the provider.
        """
        pass

    @abstractmethod
    def list_devices(self) -> List[Dict[str, Any]]:
        """
        Lists the available devices/backends for the provider.
        """
        pass

    @abstractmethod
    def get_job_status(self, job_id: str) -> str:
        """
        Gets the status of a job.

        :param job_id: The ID of the job.
        :return: The status of the job.
        """
        pass

    @abstractmethod
    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        """
        Gets the result of a job.

        :param job_id: The ID of the job.
        :return: The result of the job.
        """
        pass

    def execute_batch(self, tasks: List[Any], device_name: str, **kwargs) -> List[str]:
        """
        Executes a batch of tasks. Default implementation loops through tasks.
        Providers can override this for optimized batch execution.
        """
        # Subclasses (QuantumProvider, ClassicalProvider) provide real implementations.
        # Base class raises because it cannot determine which execute method to call.
        raise NotImplementedError("Batch execution not implemented for this provider type.")

    @property
    def max_batch_size(self) -> int:
        return 10


class QuantumProvider(BaseProvider):
    """
    An abstract base class for quantum providers.
    """

    @abstractmethod
    def execute_circuit(self, circuit: Any, device_name: str, shots: int) -> str:
        """
        Executes a quantum circuit on a specified device.
        """
        pass

    def execute_batch(self, tasks: List[Any], device_name: str, **kwargs) -> List[str]:
        """
        Default batch implementation for quantum providers: Sequential execution.
        """
        shots = kwargs.get("shots", 1024)
        return [self.execute_circuit(circuit, device_name, shots) for circuit in tasks]


class ClassicalProvider(BaseProvider):
    """
    An abstract base class for classical providers.
    """

    @abstractmethod
    def execute_task(self, task: Any, device_name: str = "default") -> str:
        """
        Executes a classical task.
        """
        pass

    def execute_batch(self, tasks: List[Any], device_name: str, **kwargs) -> List[str]:
        """
        Default batch implementation for classical providers: Sequential execution.
        """
        return [self.execute_task(task, device_name) for task in tasks]
