import json
import random
from pathlib import Path

OUT = Path("better_datasets/python_to_quantum2.jsonl")
OUT.parent.mkdir(exist_ok=True)

pairs = [
    # ------------------------------------------------------------
    # XOR GATE PATTERNS
    # ------------------------------------------------------------
    (
        "def xor(a, b):\n    return a ^ b",
        "# inputs: a, b\n# outputs: out\ncx a, out\ncx b, out"
    ),
    (
        "def xor_gate(a, b):\n    return a ^ b",
        "# inputs: a, b\n# outputs: out\ncx a, out\ncx b, out"
    ),
    (
        "def exclusive_or(x, y):\n    return x ^ y",
        "# inputs: x, y\n# outputs: out\ncx x, out\ncx y, out"
    ),
    (
        "a = 1\nb = 0\nresult = a ^ b",
        "# inputs: a, b\n# outputs: result\ncx a, result\ncx b, result"
    ),
    (
        "def bitwise_xor(bit1, bit2):\n    return bit1 ^ bit2",
        "# inputs: bit1, bit2\n# outputs: out\ncx bit1, out\ncx bit2, out"
    ),
    (
        "if a != b:\n    return 1\nelse:\n    return 0",
        "# inputs: a, b\n# outputs: out\ncx a, out\ncx b, out"
    ),
    
    # ------------------------------------------------------------
    # OR GATE PATTERNS (De Morgan's Law implementation)
    # ------------------------------------------------------------
    (
        "def or_gate(a, b):\n    return a | b",
        "# inputs: a, b\n# outputs: out\nx a\nx b\nccx a, b, out\nx out\nx a\nx b"
    ),
    (
        "def logical_or(x, y):\n    return x or y",
        "# inputs: x, y\n# outputs: out\nx x\nx y\nccx x, y, out\nx out\nx x\nx y"
    ),
    (
        "if a == 1 or b == 1:\n    return 1\nelse:\n    return 0",
        "# inputs: a, b\n# outputs: out\nx a\nx b\nccx a, b, out\nx out\nx a\nx b"
    ),
    (
        "def bitwise_or(a, b):\n    return a | b",
        "# inputs: a, b\n# outputs: out\nx a\nx b\nccx a, b, out\nx out\nx a\nx b"
    ),
    (
        "result = a | b",
        "# inputs: a, b\n# outputs: result\nx a\nx b\nccx a, b, result\nx result\nx a\nx b"
    ),
    
    # ------------------------------------------------------------
    # AND GATE PATTERNS
    # ------------------------------------------------------------
    (
        "def and_gate(a, b):\n    return a & b",
        "# inputs: a, b\n# outputs: out\nccx a, b, out"
    ),
    (
        "def logical_and(x, y):\n    return x and y",
        "# inputs: x, y\n# outputs: out\nccx x, y, out"
    ),
    (
        "if a == 1 and b == 1:\n    return 1\nelse:\n    return 0",
        "# inputs: a, b\n# outputs: out\nccx a, b, out"
    ),
    (
        "def bitwise_and(a, b):\n    return a & b",
        "# inputs: a, b\n# outputs: out\nccx a, b, out"
    ),
    (
        "result = a & b",
        "# inputs: a, b\n# outputs: result\nccx a, b, result"
    ),
    
    # ------------------------------------------------------------
    # NOT GATE PATTERNS
    # ------------------------------------------------------------
    (
        "def not_gate(bit):\n    return 1 - bit",
        "# inputs: bit\n# outputs: out\ncx bit, out\nx out"
    ),
    (
        "def invert(bit):\n    return not bit",
        "# inputs: bit\n# outputs: out\ncx bit, out\nx out"
    ),
    (
        "bit = 1\nresult = ~bit",
        "# inputs: bit\n# outputs: result\ncx bit, result\nx result"
    ),
    (
        "def not_operator(a):\n    return not a",
        "# inputs: a\n# outputs: out\ncx a, out\nx out"
    ),
    
    # ------------------------------------------------------------
    # NAND GATE PATTERNS
    # ------------------------------------------------------------
    (
        "def nand_gate(a, b):\n    return not (a and b)",
        "# inputs: a, b\n# outputs: out\nccx a, b, out\nx out"
    ),
    (
        "def nand(a, b):\n    return not (a & b)",
        "# inputs: a, b\n# outputs: out\nccx a, b, out\nx out"
    ),
    (
        "result = not (a and b)",
        "# inputs: a, b\n# outputs: result\nccx a, b, result\nx result"
    ),
    
    # ------------------------------------------------------------
    # NOR GATE PATTERNS
    # ------------------------------------------------------------
    (
        "def nor_gate(a, b):\n    return not (a or b)",
        "# inputs: a, b\n# outputs: out\nx a\nx b\nccx a, b, out\nx a\nx b"
    ),
    (
        "def nor(a, b):\n    return not (a | b)",
        "# inputs: a, b\n# outputs: out\nx a\nx b\nccx a, b, out\nx a\nx b"
    ),
    (
        "result = not (a or b)",
        "# inputs: a, b\n# outputs: result\nx a\nx b\nccx a, b, result\nx a\nx b"
    ),
    
    # ------------------------------------------------------------
    # HALF ADDER PATTERNS (for bonus marks)
    # ------------------------------------------------------------
    (
        "def half_adder(a, b):\n    sum = a ^ b\n    carry = a & b\n    return sum, carry",
        "# inputs: a, b\n# outputs: sum, carry\ncx a, sum\ncx b, sum\nccx a, b, carry"
    ),
    (
        "sum = a ^ b\ncarry = a & b",
        "# inputs: a, b\n# outputs: sum, carry\ncx a, sum\ncx b, sum\nccx a, b, carry"
    ),
    
    # ------------------------------------------------------------
    # FULL ADDER PATTERNS (optional but strong)
    # ------------------------------------------------------------
    (
        "def full_adder(a, b, cin):\n    sum = a ^ b ^ cin\n    carry = (a & b) | (cin & (a ^ b))\n    return sum, carry",
        "# inputs: a, b, cin\n# outputs: sum, carry\ncx a, sum\ncx b, sum\ncx cin, sum\nccx a, b, carry\nccx cin, sum, carry"
    ),
    (
        "sum = a ^ b ^ cin\ncarry = (a & b) | (cin & (a ^ b))",
        "# inputs: a, b, cin\n# outputs: sum, carry\ncx a, sum\ncx b, sum\ncx cin, sum\nccx a, b, carry\nccx cin, sum, carry"
    ),
    
    # ------------------------------------------------------------
    # XNOR PATTERNS (for completeness)
    # ------------------------------------------------------------
    (
        "def xnor(a, b):\n    return not (a ^ b)",
        "# inputs: a, b\n# outputs: out\ncx a, out\ncx b, out\nx out"
    ),
    (
        "result = not (a ^ b)",
        "# inputs: a, b\n# outputs: result\ncx a, result\ncx b, result\nx result"
    ),
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
        variations.append((py.replace('a, b', 'input1, input2'), q))
    
    # Add return statement variations
    if 'return' in py and 'def ' in py:
        # Change return format
        lines = py.split('\n')
        for i, line in enumerate(lines):
            if 'return' in line:
                # Add parenthesis variation
                lines[i] = line.replace('return ', 'return(') + ')'
                variations.append(('\n'.join(lines), q))
                break

with OUT.open("w") as f:
    # Generate 350 examples (optimized for 15-20 min training)
    for i in range(350):
        py, q = random.choice(variations)
        f.write(json.dumps({
            "input": "Convert the following Python logic into an equivalent quantum gate sequence:\n" + py,
            "output": q
        }) + "\n")

print("✅ Logic-level quantum dataset generated")
print(f"Total examples: 350 (optimized for 15-20 min training)")
print("Key improvements:")
print("1. Pure logic-level outputs (no imports, no Qiskit)")
print("2. Reversible & defensible quantum circuits")
print("3. Consistent format: # inputs: ... # outputs: ...")
print("4. All major gates: XOR, AND, OR, NOT, NAND, NOR")
print("5. Bonus: Half Adder & Full Adder for extra marks")
print("6. Easy to post-process into Qiskit or any framework")