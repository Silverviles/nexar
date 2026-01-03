"""Service for quantum circuit execution"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
from typing import Dict, Any

from utils.circuit_generator import circuit_generator
from services.visualization_service import visualization_service
from config.config import CIRCUIT_STYLE

class QuantumService:
    def __init__(self):
        self.simulator = Aer.get_backend('aer_simulator')
    
    def safe_execute_qc(self, qc_code: str, gate_type: str = "xor", shots: int = 1024) -> Dict[str, Any]:
        """Safely execute quantum code with fallback mechanism"""
        try:
            # Try to execute the generated code
            exec_globals = {}
            exec_locals = {
                'QuantumCircuit': QuantumCircuit,
                'Aer': Aer,
                'np': np,
                'qc': None,
                'plot_histogram': plot_histogram,
                'plt': plt
            }
            
            exec(qc_code, exec_globals, exec_locals)
            qc = exec_locals.get('qc')
            
            if qc is None or not isinstance(qc, QuantumCircuit):
                raise ValueError("Generated code did not produce a valid QuantumCircuit")
            
            # Check if circuit has measurements
            if len(qc.data) == 0 or not any(gate[0].name == 'measure' for gate in qc.data):
                qc.measure_all()
            
            return self._execute_and_analyze(qc, shots, used_generated_code=True)
            
        except Exception as e:
            print(f"Error executing generated code: {e}")
            print("Using fallback circuit...")
            
            # Use fallback circuit
            qc = circuit_generator.create_non_trivial_circuit(gate_type)
            result = self._execute_and_analyze(qc, shots, used_generated_code=False)
            result["fallback_reason"] = str(e)
            return result
    
    def _execute_and_analyze(self, qc: QuantumCircuit, shots: int, used_generated_code: bool) -> Dict[str, Any]:
        """Execute circuit and analyze results"""
        # Run the circuit
        job = self.simulator.run(qc, shots=shots)
        result = job.result()
        counts = result.get_counts(qc)
        
        # Check if circuit is trivial
        if len(counts) <= 1:
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