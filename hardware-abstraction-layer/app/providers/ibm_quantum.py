import json
from typing import List, Dict, Any, Union, Optional, Callable
import logging

from qiskit.circuit import QuantumCircuit
from qiskit.providers import BackendV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, Session, Sampler, Batch

from app.core.config import settings
from app.core.constants import BasisGates
from app.providers.base import QuantumProvider

logger = logging.getLogger(__name__)


class IBMQuantumProvider(QuantumProvider):
    """
    A quantum provider for IBM Qiskit.
    """

    def __init__(self):
        self.service = None
        try:
            if settings.IBM_QUANTUM_TOKEN:
                self.service = QiskitRuntimeService(
                    channel="ibm_quantum_platform",
                    token=settings.IBM_QUANTUM_TOKEN
                )
                logger.info("IBM Quantum Service initialized with provided token.")
            else:
                 # Fallback to default (env vars or saved account)
                self.service = QiskitRuntimeService()
                logger.info("IBM Quantum Service initialized with default credentials.")
        except Exception as e:
            logger.error(f"Failed to initialize IBM Quantum Service: {e}")
            self.service = None

    def get_provider_name(self) -> str:
        return "ibm-quantum"

    def list_devices(self) -> List[Dict[str, Any]]:
        if not self.service:
            return []
        
        try:
            backends = self.service.backends()
        except Exception as e:
            logger.error(f"Failed to fetch backends: {e}")
            return []

        devices = []
        for backend in backends:
            try:
                status = backend.status()
                is_operational = getattr(status, 'operational', True)
                pending_jobs = getattr(status, 'pending_jobs', 0)
            except Exception as e:
                logger.debug(f"Could not fetch status for backend {backend.name}: {e}")
                is_operational = True
                pending_jobs = -1

            num_qubits = getattr(backend, 'num_qubits', -1)
            # Try 'version' then 'backend_version'
            version = getattr(backend, 'version', getattr(backend, 'backend_version', "unknown"))
            is_simulator = getattr(backend, 'simulator', False)
            
            raw_basis_gates = getattr(backend, 'basis_gates', [])
            basis_gates_info = [BasisGates.get_info(g) for g in raw_basis_gates]

            coupling_map = getattr(backend, 'coupling_map', [])
            
            if hasattr(coupling_map, "get_edges"):
                 coupling_map = list(coupling_map.get_edges())
            elif not isinstance(coupling_map, list) and coupling_map is not None:
                 try:
                     coupling_map = list(coupling_map)
                 except Exception as e:
                     logger.debug(f"Coupling map not found: {e}")
                     coupling_map = [] # Failed to parse

            # Convert Edge List to Adjacency List for readability
            # Input: [[0,1], [1,0], [1,2]...]
            # Output: { "0": [1], "1": [0, 2]... }
            adjacency_map = {}
            if coupling_map:
                for edge in coupling_map:
                    if len(edge) >= 2:
                        u, v = edge[0], edge[1]
                        if u not in adjacency_map:
                            adjacency_map[u] = []
                        if v not in adjacency_map[u]:
                            adjacency_map[u].append(v)

            devices.append(
                {
                    "name": backend.name,
                    "version": version,
                    "description": getattr(backend, 'description', ""),
                    "num_qubits": num_qubits,
                    "is_simulator": is_simulator,
                    "is_operational": is_operational,
                    "pending_jobs": pending_jobs,
                    "basis_gates": basis_gates_info,
                    "coupling_map": adjacency_map,
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

        job = None
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
