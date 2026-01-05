# --- quantum.py ---

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def quantum_and(a, b):
    qa = QuantumRegister(1)
    qb = QuantumRegister(1)
    qr = QuantumRegister(1)
    cr = ClassicalRegister(1)
    qc = QuantumCircuit(qa, qb, qr, cr)

    if a: qc.x(qa[0])
    if b: qc.x(qb[0])

    qc.ccx(qa[0], qb[0], qr[0])
    qc.measure(qr[0], cr[0])

    return qc
