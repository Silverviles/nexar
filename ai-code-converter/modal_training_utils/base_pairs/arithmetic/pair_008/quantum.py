# --- quantum.py ---

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def quantum_square(x):
    qr = QuantumRegister(2)
    cr = ClassicalRegister(2)
    qc = QuantumCircuit(qr, cr)

    if x & 1: qc.x(qr[0])
    if x & 2: qc.x(qr[1])

    qc.ccx(qr[0], qr[0], qr[0])
    qc.ccx(qr[1], qr[1], qr[1])

    qc.measure(qr[0], cr[0])
    qc.measure(qr[1], cr[1])

    return qc
