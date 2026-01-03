# --- quantum.py ---

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def quantum_copy(arr):
    qsrc = QuantumRegister(len(arr))
    qdst = QuantumRegister(len(arr))
    cr = ClassicalRegister(len(arr))
    qc = QuantumCircuit(qsrc, qdst, cr)

    for i, v in enumerate(arr):
        if v:
            qc.x(qsrc[i])
        qc.cx(qsrc[i], qdst[i])

    for i in range(len(arr)):
        qc.measure(qdst[i], cr[i])

    return qc
