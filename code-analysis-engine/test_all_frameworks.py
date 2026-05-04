import requests
import json
import time

# Wait for server
time.sleep(2)

BASE_URL = "http://localhost:8002/api/v1/code-analysis-engine"

# All 5 framework test cases
tests = [
    {
        "name": "Python - Factorial",
        "framework": "python",
        "code": """def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(5))"""
    },
    {
        "name": "Qiskit - Bell State",
        "framework": "qiskit",
        "code": """from qiskit import QuantumCircuit

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()"""
    },
    {
        "name": "Cirq - Bell State",
        "framework": "cirq",
        "code": """import cirq

qubits = cirq.LineQubit.range(2)
circuit = cirq.Circuit()
circuit.append(cirq.H(qubits[0]))
circuit.append(cirq.CNOT(qubits[0], qubits[1]))
circuit.append(cirq.measure(*qubits, key='result'))"""
    },
    {
        "name": "Q# - Recursion",
        "framework": "qsharp",
        "code": """namespace Sample {
    operation RecursionExample(n : Int) : Int {
        if (n <= 1) {
            return 1;
        }
        return n * RecursionExample(n - 1);
    }
}"""
    },
    {
        "name": "OpenQASM - GHZ State",
        "framework": "openqasm",
        "code": """OPENQASM 2.0;
include "qelib1.inc";

qreg q[3];
creg c[3];

h q[0];
cx q[0], q[1];
cx q[1], q[2];
measure q -> c;"""
    }
]

results = []

print("=" * 80)
print("REAL ENDPOINT TEST - ALL 5 FRAMEWORKS")
print("=" * 80)

for test in tests:
    print(f"\n{len(results) + 1}. {test['name']}")
    print("-" * 80)
    
    try:
        resp = requests.post(
            f"{BASE_URL}/analyze",
            json={"code": test["code"]},
            timeout=30
        )
        
        status = "PASS" if resp.status_code == 200 else f"FAIL [{resp.status_code}]"
        print(f"Status: {status}")
        
        if resp.status_code == 200:
            data = resp.json()
            results.append({
                "name": test["name"],
                "framework": test["framework"],
                "status_code": 200,
                "detected_language": data.get("detected_language"),
                "language_confidence": data.get("language_confidence"),
                "is_quantum": data.get("is_quantum"),
                "detected_algorithms": data.get("detected_algorithms"),
                "algorithm_source": data.get("algorithm_detection_source"),
                "recursion": data.get("recursion", {}).get("has_recursion") if data.get("recursion") else None,
                "qubits": data.get("qubits_required", 0),
                "gates": data.get("gate_count", 0),
                "depth": data.get("circuit_depth", 0),
                "entanglement": data.get("entanglement_score", 0),
                "superposition": data.get("superposition_score", 0)
            })
            
            print(f"Language: {data.get('detected_language')} (confidence: {data.get('language_confidence'):.3f})")
            print(f"Is Quantum: {data.get('is_quantum')}")
            print(f"Algorithms: {data.get('detected_algorithms')} (source: {data.get('algorithm_detection_source')})")
            
            if data.get("recursion") and data.get("recursion", {}).get("has_recursion"):
                print(f"Recursion: YES - {data.get('recursion', {}).get('recursive_functions')}")
            
            if data.get("is_quantum"):
                print(f"Qubits: {data.get('qubits_required')}, Gates: {data.get('gate_count')}, Depth: {data.get('circuit_depth')}")
                print(f"Entanglement: {data.get('entanglement_score'):.3f}, Superposition: {data.get('superposition_score'):.3f}")
        else:
            print(f"Error: {resp.text[:200]}")
            results.append({
                "name": test["name"],
                "framework": test["framework"],
                "status_code": resp.status_code,
                "error": resp.text[:200]
            })
            
    except Exception as e:
        print(f"Exception: {e}")
        results.append({
            "name": test["name"],
            "framework": test["framework"],
            "error": str(e)
        })

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
passed = sum(1 for r in results if r.get("status_code") == 200)
failed = len(results) - passed
print(f"Passed: {passed}/{len(results)}")
print(f"Failed: {failed}/{len(results)}")

# Save results
with open("tests/all_frameworks_real_endpoint_test.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to: tests/all_frameworks_real_endpoint_test.json")
