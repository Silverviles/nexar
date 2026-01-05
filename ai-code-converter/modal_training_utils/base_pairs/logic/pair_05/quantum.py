# --- quantum.py ---

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def quantum_not(a):
    qr = QuantumRegister(1)
    cr = ClassicalRegister(1)
    qc = QuantumCircuit(qr, cr)

    if a:
        qc.x(qr[0])
    qc.x(qr[0])

    qc.measure(qr[0], cr[0])
    return qc
