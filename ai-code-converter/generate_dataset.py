import json
import random
from pathlib import Path

OUT = Path("better_datasets/python_to_quantum.jsonl")
OUT.parent.mkdir(exist_ok=True)

pairs = [
    # ------------------------------------------------------------
    # XOR GATE PATTERNS (always create superposition + entanglement)
    # ------------------------------------------------------------
    (
        "def xor(a, b):\n    return a ^ b",
        "qc = QuantumCircuit(2, 2)\nqc.h(0)\nqc.h(1)\nqc.cx(0,1)\nqc.measure([0,1],[0,1])"
    ),
    (
        "def xor_gate(a, b):\n    return a ^ b",
        "qc = QuantumCircuit(2, 2)\nqc.h(0)\nqc.h(1)\nqc.cx(0,1)\nqc.measure_all()"
    ),
    (
        "def exclusive_or(x, y):\n    return x ^ y",
        "qc = QuantumCircuit(2, 2)\nqc.h(0)\nqc.h(1)\nqc.cx(0,1)\nqc.measure([0,1],[0,1])"
    ),
    (
        "a = 1\nb = 0\nresult = a ^ b",
        "qc = QuantumCircuit(2, 2)\nqc.h(0)\nqc.h(1)\nqc.cx(0,1)\nqc.measure([0,1],[0,1])"
    ),
    (
        "def bitwise_xor(bit1, bit2):\n    return bit1 ^ bit2",
        "qc = QuantumCircuit(2, 2)\nqc.h(0)\nqc.h(1)\nqc.cx(0,1)\nqc.measure([0,1],[0,1])"
    ),
    (
        "if a != b:\n    return 1\nelse:\n    return 0",
        "qc = QuantumCircuit(2, 2)\nqc.h(0)\nqc.h(1)\nqc.cx(0,1)\nqc.measure([0,1],[0,1])"
    ),
    
    # ------------------------------------------------------------
    # OR GATE PATTERNS (superposition + OR logic)
    # ------------------------------------------------------------
    (
        "def or_gate(a, b):\n    return a | b",
        "qc = QuantumCircuit(2, 2)\nqc.h(0)\nqc.h(1)\nqc.x(0)\nqc.cx(0,1)\nqc.measure([0,1],[0,1])"
    ),
    (
        "def logical_or(x, y):\n    return x or y",
        "qc = QuantumCircuit(2, 2)\nqc.h(0)\nqc.h(1)\nqc.x(0)\nqc.cx(0,1)\nqc.measure([0,1],[0,1])"
    ),
    (
        "if a == 1 or b == 1:\n    return 1\nelse:\n    return 0",
        "qc = QuantumCircuit(2, 2)\nqc.h(0)\nqc.h(1)\nqc.x(0)\nqc.cx(0,1)\nqc.measure([0,1],[0,1])"
    ),
    (
        "def bitwise_or(a, b):\n    return a | b",
        "qc = QuantumCircuit(2, 2)\nqc.h(0)\nqc.h(1)\nqc.x(0)\nqc.cx(0,1)\nqc.measure([0,1],[0,1])"
    ),
    (
        "result = a | b",
        "qc = QuantumCircuit(2, 2)\nqc.h(0)\nqc.h(1)\nqc.x(0)\nqc.cx(0,1)\nqc.measure([0,1],[0,1])"
    ),
    
    # ------------------------------------------------------------
    # AND GATE PATTERNS (superposition + Toffoli)
    # ------------------------------------------------------------
    (
        "def and_gate(a, b):\n    return a & b",
        "qc = QuantumCircuit(3, 3)\nqc.h(0)\nqc.h(1)\nqc.ccx(0,1,2)\nqc.measure([0,1,2],[0,1,2])"
    ),
    (
        "def logical_and(x, y):\n    return x and y",
        "qc = QuantumCircuit(3, 3)\nqc.h(0)\nqc.h(1)\nqc.ccx(0,1,2)\nqc.measure([0,1,2],[0,1,2])"
    ),
    (
        "if a == 1 and b == 1:\n    return 1\nelse:\n    return 0",
        "qc = QuantumCircuit(3, 3)\nqc.h(0)\nqc.h(1)\nqc.ccx(0,1,2)\nqc.measure([0,1,2],[0,1,2])"
    ),
    (
        "def bitwise_and(a, b):\n    return a & b",
        "qc = QuantumCircuit(3, 3)\nqc.h(0)\nqc.h(1)\nqc.ccx(0,1,2)\nqc.measure([0,1,2],[0,1,2])"
    ),
    (
        "result = a & b",
        "qc = QuantumCircuit(3, 3)\nqc.h(0)\nqc.h(1)\nqc.ccx(0,1,2)\nqc.measure([0,1,2],[0,1,2])"
    ),
    
    # ------------------------------------------------------------
    # NOT GATE PATTERNS (inverter with superposition)
    # ------------------------------------------------------------
    (
        "def not_gate(bit):\n    return 1 - bit",
        "qc = QuantumCircuit(1, 1)\nqc.h(0)\nqc.x(0)\nqc.measure([0],[0])"
    ),
    (
        "def invert(bit):\n    return not bit",
        "qc = QuantumCircuit(1, 1)\nqc.h(0)\nqc.x(0)\nqc.measure([0],[0])"
    ),
    (
        "bit = 1\nresult = ~bit",
        "qc = QuantumCircuit(1, 1)\nqc.h(0)\nqc.x(0)\nqc.measure([0],[0])"
    ),
    
    # ------------------------------------------------------------
    # RANDOM/NOR Gate (for variety - always with superposition)
    # ------------------------------------------------------------
    (
        "import random\ndef random_bit():\n    return random.choice([0,1])",
        "qc = QuantumCircuit(1, 1)\nqc.h(0)\nqc.measure([0],[0])"
    ),
    (
        "def nor_gate(a, b):\n    return not (a or b)",
        "qc = QuantumCircuit(2, 2)\nqc.h(0)\nqc.h(1)\nqc.x(0)\nqc.cx(0,1)\nqc.x(0)\nqc.x(1)\nqc.measure([0,1],[0,1])"
    ),
    (
        "def nand_gate(a, b):\n    return not (a and b)",
        "qc = QuantumCircuit(3, 3)\nqc.h(0)\nqc.h(1)\nqc.ccx(0,1,2)\nqc.x(2)\nqc.measure([0,1,2],[0,1,2])"
    )
]

# ------------------------------------------------------------
# VARIATIONS - Same logic, different Python syntax
# ------------------------------------------------------------
variations = []

for py, q in pairs:
    # Keep the original
    variations.append((py, q))
    
    # Add comments variation
    variations.append((f"# Python implementation\n{py}", q))
    
    # Add simple docstring variation
    if 'def ' in py:
        func_body = py.split('\n', 1)[1] if '\n' in py else ''
        variations.append((f"def func():\n    \"\"\"Simple implementation\"\"\"\n{func_body}", q))
    
    # Add parameter name variations
    if 'a, b' in py:
        variations.append((py.replace('a, b', 'x, y'), q))
        variations.append((py.replace('a, b', 'in1, in2'), q))

with OUT.open("w") as f:
    # Generate 350 examples (optimized for 15-20 min training)
    for i in range(350):  # CHANGED FROM 500 TO 350
        py, q = random.choice(variations)
        f.write(json.dumps({
            "input": "Translate Python to quantum circuit:\n" + py,
            "output": q
        }) + "\n")

print("✅ Enhanced gate-specific dataset generated")
print(f"Total examples: 350 (optimized for 15-20 min training)")
print("Key improvements:")
print("1. Removed imports from ALL outputs (cleaner training)")
print("2. Python-only inputs (your requirement)")
print("3. Always includes superposition (solves histogram issue)")
print("4. Consistent formatting")