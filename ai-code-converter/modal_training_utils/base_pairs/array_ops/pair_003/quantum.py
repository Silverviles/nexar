# --- quantum.py ---

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def quantum_array_sum(arr):
    qr = QuantumRegister(len(arr))
    cr = ClassicalRegister(len(arr))
    qc = QuantumCircuit(qr, cr)

    for i, v in enumerate(arr):
        if v == 1:
            qc.x(qr[i])

    for i in range(len(arr)):
        qc.measure(qr[i], cr[i])

    return qc
