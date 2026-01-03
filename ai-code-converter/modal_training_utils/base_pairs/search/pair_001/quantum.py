from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
import math

def grover_search(arr, target):
    """Quantum search using Grover's algorithm"""
    n = len(arr)
    num_qubits = math.ceil(math.log2(n))
    
    # Find target index
    try:
        target_index = arr.index(target)
    except ValueError:
        return -1
    
    # Quantum circuit
    qr = QuantumRegister(num_qubits, 'q')
    cr = ClassicalRegister(num_qubits, 'c')
    qc = QuantumCircuit(qr, cr)
    
    # Initialize superposition
    qc.h(qr)
    
    # Oracle: mark target state
    binary = format(target_index, f'0{num_qubits}b')
    for i, bit in enumerate(binary):
        if bit == '0':
            qc.x(qr[i])
    
    # Multi-controlled Z
    if num_qubits > 1:
        qc.h(qr[num_qubits-1])
        qc.mcx(list(range(num_qubits-1)), qr[num_qubits-1])
        qc.h(qr[num_qubits-1])
    else:
        qc.z(qr[0])
    
    # Restore qubits
    for i, bit in enumerate(binary):
        if bit == '0':
            qc.x(qr[i])
    
    # Diffusion operator
    qc.h(qr)
    qc.x(qr)
    if num_qubits > 1:
        qc.h(qr[num_qubits-1])
        qc.mcx(list(range(num_qubits-1)), qr[num_qubits-1])
        qc.h(qr[num_qubits-1])
    else:
        qc.z(qr[0])
    qc.x(qr)
    qc.h(qr)
    
    # Measure
    qc.measure(qr, cr)
    return qc

# Example usage
numbers = [2, 5, 8, 12, 16, 23, 38, 45]
target = 23
circuit = grover_search(numbers, target)
simulator = AerSimulator()
result = simulator.run(circuit, shots=1024).result()
counts = result.get_counts()
print(f"Measurement results: {counts}")
