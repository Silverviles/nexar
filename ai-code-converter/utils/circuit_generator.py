"""Utility for generating fallback circuits"""
import numpy as np
from qiskit import QuantumCircuit
from config.config import DEFAULT_NUM_QUBITS

class CircuitGenerator:
    @staticmethod
    def create_non_trivial_circuit(gate_type: str = "xor", num_qubits: int = DEFAULT_NUM_QUBITS) -> QuantumCircuit:
        """Create a fallback circuit that gives multiple measurement outcomes"""
        qc = QuantumCircuit(num_qubits, num_qubits)
        
        # Apply different gates based on gate_type
        if gate_type.lower() == "xor":
            # Create superposition and entanglement
            for i in range(num_qubits):
                qc.h(i)
            for i in range(num_qubits - 1):
                qc.cx(i, i + 1)
            # Add some single-qubit gates for variety
            qc.rx(np.pi / 4, 0)
            qc.ry(np.pi / 3, 1)
            
        elif gate_type.lower() == "or":
            # Create superposition and OR-like behavior
            for i in range(num_qubits):
                qc.h(i)
            qc.cx(0, 1)
            qc.cx(1, 2)
            qc.x(0)
            
        elif gate_type.lower() == "and":
            # Create superposition and AND-like behavior
            for i in range(num_qubits):
                qc.h(i)
            qc.ccx(0, 1, 2)
            qc.rx(np.pi / 6, 0)
            qc.ry(np.pi / 6, 1)
            
        else:  # Default: create superposition and entanglement
            for i in range(num_qubits):
                qc.h(i)
            for i in range(num_qubits - 1):
                qc.cx(i, i + 1)
            # Add rotation gates for more variety
            for i in range(num_qubits):
                qc.rz(np.random.random() * np.pi, i)
        
        # Add measurement
        qc.measure(range(num_qubits), range(num_qubits))
        
        return qc

circuit_generator = CircuitGenerator()