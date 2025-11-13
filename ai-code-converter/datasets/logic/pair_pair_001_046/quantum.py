from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

def quantum_parity_check(number, num_bits=4):
    """Check parity (even/odd) using quantum circuit"""
    qr = QuantumRegister(num_bits, 'q')
    qr_ancilla = QuantumRegister(1, 'parity')
    cr = ClassicalRegister(1, 'result')
    
    qc = QuantumCircuit(qr, qr_ancilla, cr)
    
    # Encode number in binary
    for i in range(num_bits):
        if (number >> i) & 1:
            qc.x(qr[i])
    
    # XOR all bits into ancilla (parity)
    for i in range(num_bits):
        qc.cx(qr[i], qr_ancilla[0])
    
    # Measure ancilla: 0 = even, 1 = odd
    qc.measure(qr_ancilla[0], cr[0])
    return qc

# Example usage
num = 8
circuit = quantum_parity_check(num)
simulator = AerSimulator()
result = simulator.run(circuit, shots=1).result()
counts = result.get_counts()
measured = list(counts.keys())[0]
is_even = (measured == '0')
print(f"{num} is {'even' if is_even else 'odd'}")
