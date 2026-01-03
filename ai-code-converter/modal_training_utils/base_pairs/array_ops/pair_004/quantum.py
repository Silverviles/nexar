# --- quantum.py ---

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def quantum_array_max(arr):
    qr = QuantumRegister(len(arr))
    cr = ClassicalRegister(1)
    qc = QuantumCircuit(qr, cr)

    for i, v in enumerate(arr):
        if v:
            qc.x(qr[i])

    qc.cx(qr[0], cr[0])
    return qc
