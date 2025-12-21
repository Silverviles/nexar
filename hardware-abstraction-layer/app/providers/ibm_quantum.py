from typing import List, Dict, Any, Union, Optional, Callable

from qiskit.circuit import QuantumCircuit
from qiskit.providers import BackendV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, Session, Sampler, Batch

from app.providers.base import QuantumProvider


class IBMQuantumProvider(QuantumProvider):
    """
    A quantum provider for IBM Qiskit.
    """

    def __init__(self):
        try:
            self.service = QiskitRuntimeService()
        except Exception:
            self.service = None

    def get_provider_name(self) -> str:
        return "ibm-quantum"

    def list_devices(self) -> List[Dict[str, Any]]:
        if not self.service:
            return []
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
        if not self.service:
            raise RuntimeError("IBM Quantum Service not initialized (missing credentials).")
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

    def execute_batch(self, tasks: List[QuantumCircuit], device_name: str, **kwargs) -> List[str]:
        if not self.service:
            raise RuntimeError("IBM Quantum Service not initialized (missing credentials).")
        backend = self.service.backend(device_name)
        shots = kwargs.get("shots", 1024)
        mode = kwargs.get("mode")

        pm = generate_preset_pass_manager(target=backend.target, optimization_level=1)
        transpiled_circuits = pm.run(tasks)

        # Context manager handling
        if mode is not None:
             sampler = Sampler(mode=mode)
             job = sampler.run(transpiled_circuits, shots=shots)
        else:
            with Session(backend=backend) as session:
                sampler = Sampler(mode=session)
                job = sampler.run(transpiled_circuits, shots=shots)
        
        # Return composite IDs
        base_id = job.job_id()
        return [f"{base_id}:{i}" for i in range(len(tasks))]

    def get_job_status(self, job_id: str) -> str:
        if not self.service:
            return "UNKNOWN"
        real_id = job_id.split(":")[0]
        job = self.service.job(real_id)
        return job.status().title()

    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        if not self.service:
            return {}
        parts = job_id.split(":")
        real_id = parts[0]
        index = int(parts[1]) if len(parts) > 1 else 0

        job = self.service.job(real_id)
        result = job.result()
        
        if hasattr(result, 'pub_results') and len(result.pub_results) > index:
            pub_result = result.pub_results[index]
            return pub_result.data.meas.get_counts() if hasattr(pub_result.data, 'meas') else {}
        return {}
