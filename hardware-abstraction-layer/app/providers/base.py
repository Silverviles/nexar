from abc import ABC, abstractmethod
from typing import List, Dict, Any

class QuantumProvider(ABC):
    """
    An abstract base class for quantum providers.
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
        Lists the available quantum devices for the provider.
        """
        pass

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
