from fastapi.testclient import TestClient
import json
import runpy

# Load main.py dynamically to ensure imports work in test environment
ns = runpy.run_path('../main.py')
app = ns.get('app')
if app is None:
    raise RuntimeError('Could not load FastAPI app from main.py')

client = TestClient(app)

TESTS = [
    {
        "name": "classical_recursive_factorial",
        "code": """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

result = factorial(5)
""",
        "expected": {
            "recursion": True
        }
    },
    {
        "name": "classical_iterative_sum",
        "code": """
def sum_array(arr):
    total = 0
    for x in arr:
        total += x
    return total

result = sum_array([1,2,3])
""",
        "expected": {
            "recursion": False
        }
    },
    {
        "name": "qiskit_simple_circuit",
        "code": """
from qiskit import QuantumCircuit

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0,1)
qc.measure_all()
""",
        "expected": {
            "is_quantum": True
        }
    },
    {
        "name": "qsharp_recursive_example",
        "code": """
namespace Sample {
    operation RecursionExample(n : Int) : Int {
        if (n <= 1) {
            return 1;
        }
        return n * RecursionExample(n - 1);
    }
}
""",
        "expected": {
            "recursion": True
        }
    }
]

results = []
for t in TESTS:
    resp = client.post('/api/v1/code-analysis-engine/analyze', json={"code": t['code'], "problem_size_strategy": "loc"})
    try:
        data = resp.json()
    except Exception as e:
        data = {"error": str(e), "status_code": resp.status_code, "text": resp.text}
    print(f"Test {t['name']} -> status {resp.status_code}")
    results.append({"name": t['name'], "status_code": resp.status_code, "response": data})

with open('tests/analyze_endpoint_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print('Done. Results saved to tests/analyze_endpoint_results.json')
