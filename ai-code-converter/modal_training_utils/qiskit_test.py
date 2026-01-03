#!/usr/bin/env python3
"""Check Qiskit + Aer setup with automatic Aer detection"""

import sys

try:
    from qiskit import QuantumCircuit, transpile
    print("✅ Qiskit imported successfully!")
except ImportError as e:
    print(f"❌ Qiskit import failed: {e}")
    sys.exit(1)

# Check if Aer is available
try:
    from qiskit_aer import Aer
    aer_available = True
except ImportError:
    aer_available = False
    print("⚠️ Qiskit Aer is not installed.")
    print("   Install it with: pip install qiskit-aer")
    print("   or install the full Qiskit package: pip install qiskit[all]")

if aer_available:
    # Create a simple 2-qubit circuit (Bell state)
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])

    print(f"Circuit created: {qc.num_qubits} qubits")

    # Run simulation on Aer simulator
    simulator = Aer.get_backend('aer_simulator')

    try:
        # Try new API
        job = simulator.run(qc, shots=1000)
        result = job.result()
        counts = result.get_counts(qc)
        print("✅ Using new API (simulator.run())")
    except Exception:
        # Fallback to transpile + run
        try:
            qc_compiled = transpile(qc, simulator)
            job = simulator.run(qc_compiled, shots=1000)
            result = job.result()
            counts = result.get_counts(qc_compiled)
            print("✅ Using transpile + simulator.run()")
        except Exception as e:
            print(f"❌ Simulation failed: {e}")
            sys.exit(1)

    print("\n📊 Simulation results:")
    for state, count in counts.items():
        print(f"   |{state}⟩: {count} times")

    print("✅ Qiskit + Aer setup is working correctly!")
else:
    print("❌ Cannot run simulation because Aer is missing.")
