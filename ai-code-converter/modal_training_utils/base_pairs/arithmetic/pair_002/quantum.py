# --- quantum.py ---

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def quantum_add(a, b, n=4):
    qa = QuantumRegister(n)
    qb = QuantumRegister(n)
    qc = QuantumRegister(n)
    cr = ClassicalRegister(n+1)
    circuit = QuantumCircuit(qa, qb, qc, cr)

    for i in range(n):
        if (a >> i) & 1: circuit.x(qa[i])
        if (b >> i) & 1: circuit.x(qb[i])

    for i in range(n):
        circuit.ccx(qa[i], qb[i], qc[i])
        circuit.cx(qa[i], qb[i])
        if i < n-1:
            circuit.ccx(qb[i], qc[i], qc[i+1])

    for i in range(n):
        circuit.measure(qb[i], cr[i])
    circuit.measure(qc[n-1], cr[n])

    return circuit
