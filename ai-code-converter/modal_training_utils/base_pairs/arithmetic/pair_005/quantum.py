# --- quantum.py ---

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def quantum_increment(x, n=4):
    qr = QuantumRegister(n)
    cr = ClassicalRegister(n)
    qc = QuantumCircuit(qr, cr)

    for i in range(n):
        if (x >> i) & 1:
            qc.x(qr[i])

    qc.x(qr[0])
    for i in range(n-1):
        qc.cx(qr[i], qr[i+1])

    for i in range(n):
        qc.measure(qr[i], cr[i])

    return qc
