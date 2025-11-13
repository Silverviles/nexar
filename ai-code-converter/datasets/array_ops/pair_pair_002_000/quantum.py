from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

def quantum_sum_array(numbers, num_bits=4):
    """Sum array elements using a simple quantum adder cascade"""
    # Enough qubits for largest possible sum
    max_sum_bits = num_bits + len(numbers).bit_length()
    
    qr_accumulator = QuantumRegister(max_sum_bits, 'acc')
    qr_input = QuantumRegister(num_bits, 'input')
    cr = ClassicalRegister(max_sum_bits, 'result')
    
    qc = QuantumCircuit(qr_accumulator, qr_input, cr)
    
    # Add each number sequentially
    for number in numbers:
        # Encode number in input register
        for i in range(num_bits):
            if (number >> i) & 1:
                qc.x(qr_input[i])
        
        # Simple adder: XOR for sum, AND for carry
        for i in range(num_bits):
            qc.cx(qr_input[i], qr_accumulator[i])
            if i < num_bits - 1:
                qc.ccx(qr_input[i], qr_accumulator[i], qr_accumulator[i + 1])
        
        # Reset input register
        for i in range(num_bits):
            if (number >> i) & 1:
                qc.x(qr_input[i])
    
    # Measure accumulator
    qc.measure(qr_accumulator, cr)
    return qc

# Example usage
arr = [1, 2, 3, 4, 5]
circuit = quantum_sum_array(arr)
simulator = AerSimulator()
result = simulator.run(circuit, shots=1).result()
counts = result.get_counts()
measured = list(counts.keys())[0]
total = int(measured, 2)
print(f"Sum: {total}")
