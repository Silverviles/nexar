"""Service for quantum circuit execution"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
from typing import Dict, Any
from qiskit_aer import AerSimulator
from utils.circuit_generator import circuit_generator
from services.visualization_service import visualization_service
from config.config import CIRCUIT_STYLE
from qiskit import transpile

class QuantumService:
    def __init__(self):
        self.simulator = AerSimulator()
    def safe_execute_qc(self, qc_code: str, gate_type: str = "xor", shots: int = 1024) -> Dict[str, Any]:
        try:
            import re
            exec_globals = {}
            exec_locals = {
                'QuantumCircuit': QuantumCircuit,
                'Aer': Aer,
                'np': np,
                'qc': None,
                'plot_histogram': plot_histogram,
                'plt': plt
            }
            code_no_comments = re.sub(r'#.*', '', qc_code)  # strip comments first

        # --- Parse declared qubit count and max used index ---
            declared = re.search(r'QuantumCircuit\((\d+)', code_no_comments)
            used = re.findall(r'qc\.\w+\([^)]*\b(\d+)\b', code_no_comments)
            declared_n = int(declared.group(1)) if declared else 2
            max_used = max(int(i) for i in used) + 1 if used else declared_n
            safe_n = max(declared_n, max_used)

        # Patch the code to use the safe qubit count
            patched_code = re.sub(
             r'QuantumCircuit\(\d+,\s*\d+\)',
                f'QuantumCircuit({safe_n}, {safe_n})',
                qc_code
            )
            two_qubit_gates = ['cz', 'cx', 'cy', 'swap', 'ch', 'crz', 'crx', 'cry']
            for gate in two_qubit_gates:
                patched_code = re.sub(
                    rf'qc\.{gate}\((\d+),\s*(\d+),\s*\d+\)',
                    rf'qc.{gate}(\1, \2)',
                    patched_code
                )

            exec(patched_code, exec_globals, exec_locals)
            qc = exec_locals.get('qc')

            if qc is None or not isinstance(qc, QuantumCircuit):
                raise ValueError("No valid QuantumCircuit produced")

            if not any(instr.operation.name == 'measure' for instr in qc.data):
                qc.measure(range(qc.num_qubits), range(qc.num_clbits))

            qc = transpile(qc, self.simulator)
            return self._execute_and_analyze(qc, shots, used_generated_code=True)

        except Exception as e:
            print(f"Falling back: {e}")
            qc = circuit_generator.create_non_trivial_circuit(gate_type)
            result = self._execute_and_analyze(qc, shots, used_generated_code=False)
            result["fallback_reason"] = str(e)
            return result

    # _execute_and_analyze stays exactly the same ↓
    def _execute_and_analyze(self, qc: QuantumCircuit, shots: int, used_generated_code: bool) -> Dict[str, Any]:
        """Execute circuit and analyze results"""
        # Run the circuit
        job = self.simulator.run(qc, shots=shots)
        result = job.result()
        counts = result.get_counts(qc)
        
        counts = {k: v for k, v in counts.items() if v > 0}

        # Check if circuit is trivial
        total_shots = sum(counts.values())
        max_prob = max(counts.values()) / total_shots
        if max_prob < 0.1:  # threshold for “non-trivial” circuit
            raise ValueError("Circuit produced trivial results")
        
        # Get circuit metrics
        qc_depth = qc.depth()
        qc_width = qc.num_qubits
        qc_size = qc.size()
        qc_counts = qc.count_ops()
        execution_time = getattr(result, 'time_taken', 0.0)
        
        # Generate visualizations
        circuit_fig = qc.draw(output='mpl', style=CIRCUIT_STYLE)
        histogram_fig = visualization_service.create_enhanced_histogram(counts, shots)
        
        images = {
            "circuit_diagram": visualization_service.fig_to_base64(circuit_fig),
            "measurement_histogram": visualization_service.fig_to_base64(histogram_fig)
        }
        
        return {
            "success": True,
            "counts": counts,
            "probabilities": {k: v / shots for k, v in counts.items()},
            "performance": {
                "depth": qc_depth,
                "num_qubits": qc_width,
                "num_gates": qc_size,
                "gate_counts": dict(qc_counts),
                "execution_time_seconds": execution_time
            },
            "images": images,
            "used_generated_code": used_generated_code
        }

# Singleton instance
quantum_service = QuantumService()