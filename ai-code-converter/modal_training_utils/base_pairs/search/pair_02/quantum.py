# --- quantum.py ---

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def quantum_binary_search(n):
    qr = QuantumRegister(n)
    cr = ClassicalRegister(n)
    qc = QuantumCircuit(qr, cr)

    for i in range(n):
        qc.h(qr[i])

    for i in range(n):
        qc.measure(qr[i], cr[i])

    return qc
