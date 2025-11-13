from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

def quantum_adder(a, b, num_bits=4):
    """Quantum ripple-carry adder for two integers"""
    # Total qubits: num_bits for a, num_bits for b, num_bits for carry
    qr_a = QuantumRegister(num_bits, 'a')
    qr_b = QuantumRegister(num_bits, 'b')
    qr_carry = QuantumRegister(num_bits, 'carry')
    cr = ClassicalRegister(num_bits + 1, 'result')
    
    qc = QuantumCircuit(qr_a, qr_b, qr_carry, cr)
    
    # Encode integer a in binary
    for i in range(num_bits):
        if (a >> i) & 1:
            qc.x(qr_a[i])
    
    # Encode integer b in binary
    for i in range(num_bits):
        if (b >> i) & 1:
            qc.x(qr_b[i])
    
    # Ripple-carry adder circuit
    for i in range(num_bits):
        # Majority gate (carry generation)
        qc.ccx(qr_a[i], qr_b[i], qr_carry[i])
        qc.cx(qr_a[i], qr_b[i])
        
        if i < num_bits - 1:
            qc.ccx(qr_b[i], qr_carry[i], qr_carry[i + 1])
    
    # Measure result (stored in b register and final carry)
    for i in range(num_bits):
        qc.measure(qr_b[i], cr[i])
    qc.measure(qr_carry[num_bits - 1], cr[num_bits])
    
    return qc

# Example usage
num1 = 5
num2 = 3
circuit = quantum_adder(num1, num2)

simulator = AerSimulator()
result = simulator.run(circuit, shots=1).result()
counts = result.get_counts()
measured = list(counts.keys())[0]

decimal_result = int(measured, 2)
print(f"{num1} + {num2} = {decimal_result}")
