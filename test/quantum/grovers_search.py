# Pipeline recommendation test fixture -- expected classification: Quantum
# Grover's search over 3 qubits using Qiskit: superposition, a marked-state
# oracle, and a diffusion operator followed by measurement.

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

qr = QuantumRegister(3, "q")
cr = ClassicalRegister(3, "c")
qc = QuantumCircuit(qr, cr)

# Superposition over all 8 basis states
qc.h(qr)

# Oracle marking |111>
qc.h(qr[2])
qc.ccx(qr[0], qr[1], qr[2])
qc.h(qr[2])

# Diffusion operator
qc.h(qr)
qc.x(qr)
qc.h(qr[2])
qc.ccx(qr[0], qr[1], qr[2])
qc.h(qr[2])
qc.x(qr)
qc.h(qr)

qc.measure(qr, cr)
