# --- quantum.py ---

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def quantum_xor(a, b):
    qa = QuantumRegister(1)
    qb = QuantumRegister(1)
    cr = ClassicalRegister(1)
    qc = QuantumCircuit(qa, qb, cr)

    if a: qc.x(qa[0])
    if b: qc.x(qb[0])

    qc.cx(qa[0], qb[0])
    qc.measure(qb[0], cr[0])

    return qc
