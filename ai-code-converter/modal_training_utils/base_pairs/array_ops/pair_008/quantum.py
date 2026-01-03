# --- quantum.py ---

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def quantum_linear_search(arr, target):
    qr = QuantumRegister(len(arr))
    cr = ClassicalRegister(len(arr))
    qc = QuantumCircuit(qr, cr)

    for i, v in enumerate(arr):
        if v == target:
            qc.x(qr[i])

    for i in range(len(arr)):
        qc.measure(qr[i], cr[i])

    return qc
