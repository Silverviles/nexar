# --- quantum.py ---

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def quantum_subtract(a, b, n=4):
    qa = QuantumRegister(n)
    qb = QuantumRegister(n)
    cr = ClassicalRegister(n)
    qc = QuantumCircuit(qa, qb, cr)

    for i in range(n):
        if (a >> i) & 1: qc.x(qa[i])
        if (b >> i) & 1: qc.x(qb[i])

    # Two’s complement of b
    for i in range(n):
        qc.x(qb[i])
        qc.cx(qb[i], qa[i])

    for i in range(n):
        qc.measure(qa[i], cr[i])

    return qc
