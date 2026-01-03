# --- quantum.py ---

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def quantum_find_true(arr):
    qr = QuantumRegister(len(arr))
    cr = ClassicalRegister(len(arr))
    qc = QuantumCircuit(qr, cr)

    for i, v in enumerate(arr):
        if v:
            qc.x(qr[i])

    for i in range(len(arr)):
        qc.measure(qr[i], cr[i])

    return qc
