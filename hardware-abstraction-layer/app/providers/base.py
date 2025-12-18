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


class QuantumProvider(BaseProvider):
    """
    An abstract base class for quantum providers.
    """

    @abstractmethod
    def execute_circuit(self, circuit: Any, device_name: str, shots: int) -> str:
        """
        Executes a quantum circuit on a specified device.

        :param circuit: The quantum circuit to execute.
        :param device_name: The name of the device to execute the circuit on.
        :param shots: The number of times to run the circuit.
        :return: The ID of the job.
        """
        pass


class ClassicalProvider(BaseProvider):
    """
    An abstract base class for classical providers.
    """

    @abstractmethod
    def execute_task(self, task: Any, device_name: str = "default") -> str:
        """
        Executes a classical task.

        :param task: The task to execute (e.g., code, parameters).
        :param device_name: Optional device/environment specifier.
        :return: The ID of the job.
        """
        pass
