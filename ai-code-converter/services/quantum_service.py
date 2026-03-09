"""Service for quantum circuit execution (local AerSimulator or remote HAL)."""

import logging
from typing import Any, Dict, Optional

import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer, AerSimulator
from qiskit.visualization import plot_histogram

from config.config import CIRCUIT_STYLE, HAL_ENABLED, HAL_DEFAULT_DEVICE
from services.hal_client import hal_client, HALError
from services.visualization_service import visualization_service
from utils.circuit_generator import circuit_generator

logger = logging.getLogger(__name__)


class QuantumService:
    def __init__(self):
        self.simulator = AerSimulator()

    # -- public entry point ---------------------------------------------------

    async def safe_execute_qc(
        self,
        qc_code: str,
        gate_type: str = "xor",
        shots: int = 1024,
        backend: str = "local",
        device_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute quantum code on the chosen backend with fallback."""
        use_hal = backend == "hal"

        if use_hal and not HAL_ENABLED:
            raise ValueError(
                "HAL backend requested but HAL_ENABLED is not set to true"
            )

        try:
            if use_hal:
                return await self._execute_via_hal(
                    qc_code, shots, device_name or HAL_DEFAULT_DEVICE
                )
            return self._execute_locally(qc_code, shots)
        except HALError:
            raise
        except Exception as e:
            logger.warning("Error executing generated code: %s — using fallback", e)
            qc = circuit_generator.create_non_trivial_circuit(gate_type)
            result = self._run_and_analyze(qc, shots, used_generated_code=False)
            result["fallback_reason"] = str(e)
            result["backend_used"] = "local"
            return result

    # -- local execution path -------------------------------------------------

    def _execute_locally(self, qc_code: str, shots: int) -> Dict[str, Any]:
        """Build + run the circuit on the local AerSimulator."""
        qc = self._build_circuit(qc_code)
        qc = transpile(qc, self.simulator)
        result = self._run_and_analyze(qc, shots, used_generated_code=True)
        result["backend_used"] = "local"
        return result

    # -- HAL execution path ---------------------------------------------------

    async def _execute_via_hal(
        self, qc_code: str, shots: int, device_name: str
    ) -> Dict[str, Any]:
        """Send the code to the HAL and wait for results.

        The HAL's ``execute-python`` endpoint expects the submitted code
        to define a variable called ``circuit``.  The ai-code-converter
        convention is ``qc``, so we append a mapping line.
        """
        hal_code = qc_code.rstrip() + "\ncircuit = qc\n"

        raw_result = await hal_client.execute_and_wait(
            code=hal_code,
            device_name=device_name,
            shots=shots,
        )

        counts: Dict[str, int] = raw_result.get("counts", raw_result)

        qc = self._build_circuit(qc_code)
        result = self._analyze_counts(
            qc, counts, shots, used_generated_code=True
        )
        result["backend_used"] = "hal"
        result["device_name"] = device_name
        return result

    # -- shared helpers -------------------------------------------------------

    def _build_circuit(self, qc_code: str) -> QuantumCircuit:
        """Exec user code and return the resulting QuantumCircuit."""
        exec_globals: Dict[str, Any] = {}
        exec_locals: Dict[str, Any] = {
            "QuantumCircuit": QuantumCircuit,
            "Aer": Aer,
            "np": np,
            "qc": None,
            "plot_histogram": plot_histogram,
            "plt": plt,
        }

        exec(qc_code, exec_globals, exec_locals)
        qc = exec_locals.get("qc")

        if qc is None or not isinstance(qc, QuantumCircuit):
            raise ValueError("Generated code did not produce a valid QuantumCircuit")

        if len(qc.data) == 0 or not any(
            gate[0].name == "measure" for gate in qc.data
        ):
            qc.measure(
                list(range(qc.num_qubits)), list(range(qc.num_clbits))
            )

        return qc

    def _run_and_analyze(
        self, qc: QuantumCircuit, shots: int, used_generated_code: bool
    ) -> Dict[str, Any]:
        """Run locally on AerSimulator and analyse."""
        job = self.simulator.run(qc, shots=shots)
        result = job.result()
        counts = result.get_counts(qc)
        execution_time = getattr(result, "time_taken", 0.0)

        return self._analyze_counts(
            qc,
            counts,
            shots,
            used_generated_code,
            execution_time=execution_time,
        )

    def _analyze_counts(
        self,
        qc: QuantumCircuit,
        counts: Dict[str, int],
        shots: int,
        used_generated_code: bool,
        execution_time: float = 0.0,
    ) -> Dict[str, Any]:
        """Produce a uniform response dict from raw measurement counts."""
        total_shots = sum(counts.values())
        max_prob = max(counts.values()) / total_shots
        if max_prob < 0.25:
            raise ValueError("Circuit produced trivial results")

        circuit_fig = qc.draw(output="mpl", style=CIRCUIT_STYLE)
        histogram_fig = visualization_service.create_enhanced_histogram(counts, shots)

        images = {
            "circuit_diagram": visualization_service.fig_to_base64(circuit_fig),
            "measurement_histogram": visualization_service.fig_to_base64(histogram_fig),
        }

        return {
            "success": True,
            "counts": counts,
            "probabilities": {k: v / total_shots for k, v in counts.items()},
            "performance": {
                "depth": qc.depth(),
                "num_qubits": qc.num_qubits,
                "num_gates": qc.size(),
                "gate_counts": dict(qc.count_ops()),
                "execution_time_seconds": execution_time,
            },
            "images": images,
            "used_generated_code": used_generated_code,
        }


quantum_service = QuantumService()
