# --- quantum.py ---

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def quantum_reverse(arr):
    n = len(arr)
    qr = QuantumRegister(n)
    cr = ClassicalRegister(n)
    qc = QuantumCircuit(qr, cr)

    for i, v in enumerate(arr):
        if v:
            qc.x(qr[i])

    for i in range(n // 2):
        qc.swap(qr[i], qr[n - i - 1])

    for i in range(n):
        qc.measure(qr[i], cr[i])

    return qc
