from typing import List, Dict, Any, Union, Optional, Callable

from qiskit.circuit import QuantumCircuit
from qiskit.providers import BackendV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, Session, Sampler, Batch

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

    def execute_circuit(
            self,
            circuit: QuantumCircuit,
            device_name: str,
            shots: int,
            mode: Optional[Union[BackendV2, Session, Batch]] = None,
    ) -> Callable[[], str]:
        backend = self.service.backend(device_name)

        pm = generate_preset_pass_manager(target=backend.target, optimization_level=1)
        transpiled_circuit = pm.run(circuit)

        # If caller provided an explicit mode, use it directly.
        if mode is not None:
            sampler = Sampler(mode=mode)
            job = sampler.run([transpiled_circuit], shots=shots)
            return job.job_id

        # Default: session execution mode (keeps current behavior).
        with Session(backend=backend) as session:
            sampler = Sampler(mode=session)
            job = sampler.run([transpiled_circuit], shots=shots)
            return job.job_id

    def get_job_status(self, job_id: str) -> str:
        job = self.service.job(job_id)
        return job.status().title()

    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        job = self.service.job(job_id)
        result = job.result()
        if hasattr(result, 'pub_results') and result.pub_results:
            return result.pub_results[0].data.meas.get_counts() if hasattr(result.pub_results[0].data, 'meas') else {}
        return {}
