# --- quantum.py ---

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def quantum_contains(arr, target):
    qr = QuantumRegister(len(arr))
    cr = ClassicalRegister(1)
    qc = QuantumCircuit(qr, cr)

    for i, v in enumerate(arr):
        if v == target:
            qc.x(qr[i])

    qc.cx(qr[0], cr[0])
    return qc
