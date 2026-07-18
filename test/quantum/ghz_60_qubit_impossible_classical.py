# Pipeline recommendation test fixture -- expected classification: Quantum
# (FORCE_QUANTUM via the decision engine's physical-necessity override)
#
# 60-qubit GHZ (cat) state. This deliberately sits in the "memory wall" band
# (50-127 qubits, see decision-engine/services/rule_service.py STEP 0):
#   - Exact classical state-vector simulation needs 2^60 complex amplitudes
#     (~18 exabytes at 16 bytes/amplitude) -- infeasible on any classical
#     machine.
#   - 60 qubits is still within the 127-qubit IBM Eagle hardware limit, so
#     quantum execution is the only physically viable path (not a REJECT).
# The circuit itself stays shallow (depth ~= n, cx_ratio low) so it clears
# the safety-constraint checks (circuit volume / noise sensitivity) too,
# though those are skipped entirely once the qubit-count override fires.

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

N_QUBITS = 60

qr = QuantumRegister(N_QUBITS, "q")
cr = ClassicalRegister(N_QUBITS, "c")
qc = QuantumCircuit(qr, cr)

# Superposition on the first qubit
qc.h(qr[0])

# Chain of CNOTs entangles all 60 qubits into a single GHZ state:
# (|00...0> + |11...1>) / sqrt(2)
for i in range(N_QUBITS - 1):
    qc.cx(qr[i], qr[i + 1])

qc.measure(qr, cr)
