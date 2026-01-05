# --- quantum.py ---

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def quantum_multiply(a, b):
    qa = QuantumRegister(2)
    qb = QuantumRegister(2)
    qr = QuantumRegister(4)
    cr = ClassicalRegister(4)
    qc = QuantumCircuit(qa, qb, qr, cr)

    if a & 1: qc.x(qa[0])
    if a & 2: qc.x(qa[1])
    if b & 1: qc.x(qb[0])
    if b & 2: qc.x(qb[1])

    qc.ccx(qa[0], qb[0], qr[0])
    qc.ccx(qa[1], qb[0], qr[1])
    qc.ccx(qa[0], qb[1], qr[1])
    qc.ccx(qa[1], qb[1], qr[2])

    for i in range(4):
        qc.measure(qr[i], cr[i])

    return qc
