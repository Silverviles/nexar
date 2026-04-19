from typing import List, Dict, Any, Union, Optional
import logging
import signal
import statistics
import time

from qiskit.circuit import QuantumCircuit
from qiskit.providers import BackendV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, Session, Sampler, Batch
from qiskit_ibm_runtime.exceptions import RuntimeJobNotFound

from app.core.config import settings
from app.core.constants import BasisGates
from app.providers.base import QuantumProvider
from app.models.execution import DeviceAvailability

logger = logging.getLogger(__name__)


class SandboxTimeoutError(Exception):
    """Raised when sandboxed code execution times out."""
    pass


_IBM_STATUS_MAP = {
    "Initializing": "PENDING",
    "Queued": "QUEUED",
    "Validating": "QUEUED",
    "Running": "RUNNING",
    "Done": "COMPLETED",
    "Error": "FAILED",
    "Cancelled": "CANCELLED",
}


class IBMQuantumProvider(QuantumProvider):
    """
    A quantum provider for IBM Qiskit.
    """

    # Calibration cache TTL: 1 hour (IBM recalibrates ~daily)
    _CALIBRATION_CACHE_TTL = 3600

    def __init__(self):
        self.service = None
        self._calibration_cache: Dict[str, Dict[str, Any]] = {}
        self._calibration_cache_time: float = 0.0

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
                status = getattr(backend, 'status', lambda: None)()
                if status is None:
                    is_operational = True
                    pending_jobs = 0
                else:
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
                 coupling_map = list(coupling_map.get_edges())  # pyright: ignore[reportAttributeAccessIssue]
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

            # Extract calibration data (cached)
            calibration = self._get_calibration(backend)

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
                    "calibration": calibration,
                }
            )
        return devices

    def _get_calibration(self, backend: Any) -> Dict[str, Any]:
        """
        Extract median calibration metrics from a backend.
        Uses an in-memory cache with 1-hour TTL to avoid repeated slow fetches.

        Returns dict with:
          median_cx_error, median_sx_error, median_readout_error,
          median_t1_us, median_t2_us, median_gate_time_ns
        """
        name = getattr(backend, 'name', 'unknown')

        # Check cache
        now = time.time()
        if (
            name in self._calibration_cache
            and (now - self._calibration_cache_time) < self._CALIBRATION_CACHE_TTL
        ):
            return self._calibration_cache[name]

        calibration = self._extract_calibration(backend)
        self._calibration_cache[name] = calibration
        self._calibration_cache_time = now

        return calibration

    @staticmethod
    def _extract_calibration(backend: Any) -> Dict[str, Any]:
        """
        Extract median error rates and coherence times from backend.target
        and backend.qubit_properties().
        """
        empty = {
            "median_cx_error": None,
            "median_sx_error": None,
            "median_readout_error": None,
            "median_t1_us": None,
            "median_t2_us": None,
            "median_gate_time_ns": None,
        }

        target = getattr(backend, 'target', None)
        if target is None:
            return empty

        try:
            op_names = target.operation_names

            # Two-qubit gate errors (ECR, CX, or CZ — whichever the device uses)
            cx_errors: list[float] = []
            gate_times_ns: list[float] = []
            for gate_name in ['ecr', 'cx', 'cz']:
                if gate_name not in op_names:
                    continue
                for qargs, props in target[gate_name].items():
                    if props is None:
                        continue
                    if props.error is not None:
                        cx_errors.append(props.error)
                    if props.duration is not None:
                        gate_times_ns.append(props.duration * 1e9)

            # Single-qubit gate errors (SX is the standard single-qubit gate)
            sx_errors: list[float] = []
            for gate_name in ['sx', 'x', 'rz']:
                if gate_name not in op_names:
                    continue
                for qargs, props in target[gate_name].items():
                    if props is None:
                        continue
                    if props.error is not None:
                        sx_errors.append(props.error)
                if sx_errors:
                    break  # Use the first gate type that has data

            # Readout errors
            readout_errors: list[float] = []
            if 'measure' in op_names:
                for qargs, props in target['measure'].items():
                    if props is not None and props.error is not None:
                        readout_errors.append(props.error)

            # T1/T2 coherence times from qubit properties
            t1_values: list[float] = []
            t2_values: list[float] = []
            num_qubits = getattr(backend, 'num_qubits', 0)
            for i in range(num_qubits):
                try:
                    qp = backend.qubit_properties(i)
                    if qp is None:
                        continue
                    if qp.t1 is not None:
                        t1_values.append(qp.t1 * 1e6)  # seconds → microseconds
                    if qp.t2 is not None:
                        t2_values.append(qp.t2 * 1e6)
                except Exception:
                    continue

            result = {
                "median_cx_error": statistics.median(cx_errors) if cx_errors else None,
                "median_sx_error": statistics.median(sx_errors) if sx_errors else None,
                "median_readout_error": statistics.median(readout_errors) if readout_errors else None,
                "median_t1_us": round(statistics.median(t1_values), 2) if t1_values else None,
                "median_t2_us": round(statistics.median(t2_values), 2) if t2_values else None,
                "median_gate_time_ns": round(statistics.median(gate_times_ns), 2) if gate_times_ns else None,
            }

            logger.info(
                "Calibration extracted for %s: cx_err=%.4f, sx_err=%.5f, ro_err=%.4f, T1=%.1fμs, T2=%.1fμs",
                getattr(backend, 'name', '?'),
                result['median_cx_error'] or 0,
                result['median_sx_error'] or 0,
                result['median_readout_error'] or 0,
                result['median_t1_us'] or 0,
                result['median_t2_us'] or 0,
            )
            return result

        except Exception as e:
            logger.warning("Failed to extract calibration for %s: %s", getattr(backend, 'name', '?'), e)
            return empty

    def execute_circuit(
            self,
            circuit: QuantumCircuit,
            device_name: str,
            shots: int,
            mode: Optional[Union[BackendV2, Session, Batch]] = None,
    ) -> str:
        if not self.service:
            raise RuntimeError("IBM Quantum Service not initialized (missing credentials).")
        backend = self.service.backend(device_name)

        pm = generate_preset_pass_manager(target=backend.target, optimization_level=1)
        transpiled_circuit = pm.run(circuit)

        if mode is not None:
            sampler = Sampler(mode=mode)
            job = sampler.run([transpiled_circuit], shots=shots)
            return job.job_id()

        if settings.IBM_EXECUTION_MODE == "session":
            with Session(backend=backend) as session:
                sampler = Sampler(mode=session)
                job = sampler.run([transpiled_circuit], shots=shots)
                return job.job_id()

        sampler = Sampler(mode=backend)
        job = sampler.run([transpiled_circuit], shots=shots)
        return job.job_id()

    def execute_batch(self, tasks: List[QuantumCircuit], device_name: str, **kwargs) -> List[str]:
        if not self.service:
            raise RuntimeError("IBM Quantum Service not initialized (missing credentials).")
        backend = self.service.backend(device_name)
        shots = kwargs.get("shots", 1024)
        mode = kwargs.get("mode")

        pm = generate_preset_pass_manager(target=backend.target, optimization_level=1)
        transpiled_circuits = pm.run(tasks)

        if mode is not None:
            sampler = Sampler(mode=mode)
        elif settings.IBM_EXECUTION_MODE == "session":
            session = Session(backend=backend)
            sampler = Sampler(mode=session)
        else:
            sampler = Sampler(mode=backend)

        job = sampler.run(transpiled_circuits, shots=shots)

        base_id = job.job_id()
        return [f"{base_id}:{i}" for i in range(len(tasks))]

    def get_job_status(self, job_id: str) -> str:
        if not self.service:
            return "UNKNOWN"
        real_id = job_id.split(":")[0]
        try:
            job = self.service.job(real_id)
            raw = job.status().title()
            return _IBM_STATUS_MAP.get(raw, raw.upper())
        except RuntimeJobNotFound:
            logger.warning("IBM job not found while checking status: %s", real_id)
            return "UNKNOWN"

    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        if not self.service:
            return {}
        parts = job_id.split(":")
        real_id = parts[0]
        index = int(parts[1]) if len(parts) > 1 else 0

        try:
            job = self.service.job(real_id)
            result = job.result()
        except RuntimeJobNotFound:
            logger.warning("IBM job not found while fetching result: %s", real_id)
            return {}

        counts = self._extract_counts_from_result(result, index)
        if not counts:
            logger.warning(
                "IBM job %s completed but no counts could be extracted from result type %s",
                real_id,
                type(result).__name__,
            )
        return counts

    def _extract_counts_from_result(self, result: Any, index: int) -> Dict[str, Any]:
        pub_results = getattr(result, "pub_results", None)
        if pub_results is None:
            try:
                pub_results = list(result)
            except TypeError:
                pub_results = None

        if not pub_results or len(pub_results) <= index:
            return {}

        return self._extract_counts_from_pub_result(pub_results[index])

    def _extract_counts_from_pub_result(self, pub_result: Any) -> Dict[str, Any]:
        data = getattr(pub_result, "data", None)
        if data is not None:
            for register_name in ("meas", "c"):
                register = getattr(data, register_name, None)
                if register is not None and hasattr(register, "get_counts"):
                    counts = register.get_counts()
                    if counts:
                        return counts

            for value in vars(data).values():
                if hasattr(value, "get_counts"):
                    counts = value.get_counts()
                    if counts:
                        return counts

        if hasattr(pub_result, "join_data"):
            try:
                joined = pub_result.join_data()
                if hasattr(joined, "get_counts"):
                    counts = joined.get_counts()
                    if counts:
                        return counts
            except Exception as exc:
                logger.debug("Failed to extract counts via join_data(): %s", exc)

        return {}

    def check_device_availability(self, device_name: str) -> DeviceAvailability:
        """
        Check if a specific device is available for job submission.

        Returns DeviceAvailability with is_available computed based on:
        - is_operational: Device is online and accepting jobs
        - pending_jobs: Number of jobs in queue vs DEVICE_QUEUE_THRESHOLD
        """
        if not self.service:
            return DeviceAvailability(
                device_name=device_name,
                is_operational=False,
                pending_jobs=-1,
                queue_threshold=settings.DEVICE_QUEUE_THRESHOLD
            )

        try:
            backend = self.service.backend(device_name)
            status = getattr(backend, 'status', lambda: None)()
            is_operational = getattr(status, 'operational', True) if status else True
            pending_jobs = getattr(status, 'pending_jobs', 0) if status else 0

            return DeviceAvailability(
                device_name=device_name,
                is_operational=is_operational,
                pending_jobs=pending_jobs,
                queue_threshold=settings.DEVICE_QUEUE_THRESHOLD
            )
        except Exception as e:
            logger.error(f"Failed to check availability for {device_name}: {e}")
            return DeviceAvailability(
                device_name=device_name,
                is_operational=False,
                pending_jobs=-1,
                queue_threshold=settings.DEVICE_QUEUE_THRESHOLD
            )

    def execute_python_code(
        self,
        code: str,
        device_name: str,
        shots: int = 1024
    ) -> str:
        """
        Execute user-submitted Python code in a sandboxed environment.

        The code must define a 'circuit' variable that is a QuantumCircuit.
        Pre-loaded namespace includes: qiskit, QuantumCircuit, numpy, math.

        Security: Dangerous builtins are restricted (no open, eval, exec, __import__ for arbitrary modules).

        Args:
            code: Python code string that defines a 'circuit' variable
            device_name: IBM Quantum backend name
            shots: Number of measurement shots

        Returns:
            job_id: The provider job ID

        Raises:
            RuntimeError: If service not initialized
            ValueError: If code doesn't define 'circuit' or defines invalid circuit
            SandboxTimeoutError: If code execution exceeds timeout
        """
        if not self.service:
            raise RuntimeError("IBM Quantum Service not initialized (missing credentials).")

        # Build sandboxed namespace with allowed imports
        sandbox_globals = self._create_sandbox_namespace()
        sandbox_locals = {}

        # Execute code with timeout
        circuit = self._execute_sandboxed_code(code, sandbox_globals, sandbox_locals)

        # Now execute the circuit normally
        return self.execute_circuit(circuit, device_name, shots)

    def _create_sandbox_namespace(self) -> Dict[str, Any]:
        """
        Create a restricted namespace for sandboxed code execution.

        Allows: qiskit modules, numpy, math
        Blocks: open, eval, exec, compile, __import__ (restricted)
        """
        import builtins
        import math

        # Build a restricted __import__ that only permits allowed modules.
        # Without this, any `import` statement in user code raises ImportError
        # even for modules that are already pre-loaded in the sandbox namespace.
        allowed_mod_set = set(m.strip() for m in allowed_modules)

        def _restricted_import(
            name: str,
            glbls=None,
            lcls=None,
            fromlist: tuple = (),
            level: int = 0,
        ):
            base = name.split('.')[0]
            if base not in allowed_mod_set:
                raise ImportError(
                    f"Import of '{name}' is not permitted in the sandbox. "
                    f"Allowed modules: {sorted(allowed_mod_set)}"
                )
            return builtins.__import__(name, glbls, lcls, fromlist, level)

        # Create restricted builtins
        safe_builtins: Dict[str, Any] = {
            '__import__': _restricted_import,
            'abs': builtins.abs,
            'all': builtins.all,
            'any': builtins.any,
            'bin': builtins.bin,
            'bool': builtins.bool,
            'chr': builtins.chr,
            'complex': builtins.complex,
            'dict': builtins.dict,
            'divmod': builtins.divmod,
            'enumerate': builtins.enumerate,
            'filter': builtins.filter,
            'float': builtins.float,
            'format': builtins.format,
            'frozenset': builtins.frozenset,
            'hash': builtins.hash,
            'hex': builtins.hex,
            'int': builtins.int,
            'isinstance': builtins.isinstance,
            'issubclass': builtins.issubclass,
            'iter': builtins.iter,
            'len': builtins.len,
            'list': builtins.list,
            'map': builtins.map,
            'max': builtins.max,
            'min': builtins.min,
            'next': builtins.next,
            'oct': builtins.oct,
            'ord': builtins.ord,
            'pow': builtins.pow,
            'print': builtins.print,  # Allow print for debugging
            'range': builtins.range,
            'repr': builtins.repr,
            'reversed': builtins.reversed,
            'round': builtins.round,
            'set': builtins.set,
            'slice': builtins.slice,
            'sorted': builtins.sorted,
            'str': builtins.str,
            'sum': builtins.sum,
            'tuple': builtins.tuple,
            'type': builtins.type,
            'zip': builtins.zip,
            'True': True,
            'False': False,
            'None': None,
        }

        # Import allowed modules
        allowed_modules = settings.SANDBOX_ALLOWED_MODULES.split(',')
        namespace: Dict[str, Any] = {
            '__builtins__': safe_builtins,
        }

        # Pre-load Qiskit components
        if 'qiskit' in allowed_modules:
            from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
            from qiskit.circuit import Parameter
            namespace.update({
                'QuantumCircuit': QuantumCircuit,
                'QuantumRegister': QuantumRegister,
                'ClassicalRegister': ClassicalRegister,
                'Parameter': Parameter,
            })

        # Pre-load numpy
        if 'numpy' in allowed_modules:
            try:
                import numpy as np
                namespace['np'] = np
                namespace['numpy'] = np
            except ImportError:
                logger.warning("numpy not available for sandbox")

        # Pre-load math
        if 'math' in allowed_modules:
            namespace['math'] = math
            # Also expose common math functions directly
            namespace['pi'] = math.pi
            namespace['sqrt'] = math.sqrt
            namespace['sin'] = math.sin
            namespace['cos'] = math.cos
            namespace['exp'] = math.exp

        return namespace

    def _execute_sandboxed_code(
        self,
        code: str,
        sandbox_globals: Dict[str, Any],
        sandbox_locals: Dict[str, Any]
    ) -> QuantumCircuit:
        """
        Execute code in sandbox and extract the circuit variable.

        Raises:
            ValueError: If code doesn't define 'circuit' or it's not a QuantumCircuit
            SandboxTimeoutError: If execution times out
        """
        timeout = settings.PYTHON_EXEC_TIMEOUT

        def timeout_handler(signum, frame):
            raise SandboxTimeoutError(f"Code execution exceeded {timeout} seconds timeout")

        # Set timeout (Unix only - on Windows this is a no-op)
        old_handler = None
        if hasattr(signal, 'SIGALRM'):
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)

        try:
            # Compile and execute
            compiled_code = compile(code, '<user_code>', 'exec')
            exec(compiled_code, sandbox_globals, sandbox_locals)

            # Extract circuit
            if 'circuit' not in sandbox_locals:
                raise ValueError(
                    "Code must define a 'circuit' variable. "
                    "Example: circuit = QuantumCircuit(2, 2)"
                )

            circuit = sandbox_locals['circuit']
            if not isinstance(circuit, QuantumCircuit):
                raise ValueError(
                    f"'circuit' must be a QuantumCircuit, got {type(circuit).__name__}"
                )

            return circuit

        except SandboxTimeoutError:
            raise
        except SyntaxError as e:
            raise ValueError(f"Syntax error in user code: {e}")
        except Exception as e:
            raise ValueError(f"Error executing user code: {e}")
        finally:
            # Restore signal handler
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
                if old_handler:
                    signal.signal(signal.SIGALRM, old_handler)

