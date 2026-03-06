import json
import random
import re
from pathlib import Path

OUT = Path("better_datasets/python_to_quantum3.jsonl")
OUT.parent.mkdir(exist_ok=True)

# ============================================================
# QUANTUM CIRCUIT TARGETS
# ============================================================

GROVER = (
    "# Grover's algorithm: 2-qubit search, target |11>\n"
    "qc = QuantumCircuit(2, 2)\n"
    "qc.h([0, 1])\n"
    "qc.cz(0, 1)\n"
    "qc.h([0, 1])\n"
    "qc.x([0, 1])\n"
    "qc.cz(0, 1)\n"
    "qc.x([0, 1])\n"
    "qc.h([0, 1])\n"
    "qc.measure([0, 1], [0, 1])"
)

HADAMARD_RANDOM = (
    "# True randomness via Hadamard superposition\n"
    "qc = QuantumCircuit(1, 1)\n"
    "qc.h(0)\n"
    "qc.measure(0, 0)"
)

DEUTSCH = (
    "# Deutsch's algorithm: decides constant vs balanced in 1 query\n"
    "qc = QuantumCircuit(2, 1)\n"
    "qc.x(1)\n"
    "qc.h(0)\n"
    "qc.h(1)\n"
    "qc.cx(0, 1)\n"
    "qc.h(0)\n"
    "qc.measure(0, 0)"
)

BERNSTEIN_VAZIRANI = (
    "# Bernstein-Vazirani: recover secret='101' in 1 query (3 qubits)\n"
    "qc = QuantumCircuit(4, 3)\n"
    "qc.x(3)\n"
    "qc.h(3)\n"
    "qc.h([0, 1, 2])\n"
    "qc.cx(0, 3)\n"
    "qc.cx(2, 3)\n"
    "qc.h([0, 1, 2])\n"
    "qc.measure([0, 1, 2], [0, 1, 2])"
)

QUANTUM_SWAP = (
    "# Quantum SWAP via 3 CNOT gates\n"
    "qc = QuantumCircuit(2, 2)\n"
    "qc.x(0)\n"
    "qc.cx(0, 1)\n"
    "qc.cx(1, 0)\n"
    "qc.cx(0, 1)\n"
    "qc.measure([0, 1], [0, 1])"
)

TELEPORTATION = (
    "# Quantum teleportation: transfer qubit state using entanglement\n"
    "qc = QuantumCircuit(3, 2)\n"
    "qc.x(0)\n"
    "qc.h(1)\n"
    "qc.cx(1, 2)\n"
    "qc.cx(0, 1)\n"
    "qc.h(0)\n"
    "qc.measure([0, 1], [0, 1])\n"
    "qc.cx(1, 2)\n"
    "qc.cz(0, 2)"
)

# ============================================================
# BASE EXAMPLES
# ============================================================

base_pairs = [
    # LINEAR SEARCH -> GROVER
    ("def linear_search(lst, target):\n    for i, val in enumerate(lst):\n        if val == target:\n            return i\n    return -1", GROVER),
    ("def search(items, target):\n    for index in range(len(items)):\n        if items[index] == target:\n            return index\n    return -1", GROVER),
    ("def find_element(arr, x):\n    for i in range(len(arr)):\n        if arr[i] == x:\n            return i\n    return None", GROVER),

    # COIN FLIP -> HADAMARD
    ("import random\ndef coin_flip():\n    return random.choice([0, 1])", HADAMARD_RANDOM),
    ("import random\ndef random_bit():\n    return random.randint(0, 1)", HADAMARD_RANDOM),
    ("def flip_coin():\n    return 0 if random.random() < 0.5 else 1", HADAMARD_RANDOM),

    # PARITY CHECK -> DEUTSCH
    ("def is_constant(f):\n    return f(0) == f(1)", DEUTSCH),
    ("def check_function(func):\n    val0 = func(0)\n    val1 = func(1)\n    if val0 == val1:\n        return 'constant'\n    else:\n        return 'balanced'", DEUTSCH),
    ("def two_query_check(f):\n    a = f(0)\n    b = f(1)\n    return a == b", DEUTSCH),

    # HIDDEN BITSTRING -> BERNSTEIN-VAZIRANI
    ("def find_secret(oracle, n):\n    secret = []\n    for i in range(n):\n        secret.append(oracle(1 << i))\n    return secret", BERNSTEIN_VAZIRANI),
    ("def recover_bitstring(f, length):\n    bits = []\n    for i in range(length):\n        probe = [0] * length\n        probe[i] = 1\n        bits.append(f(probe))\n    return bits", BERNSTEIN_VAZIRANI),
    ("def bit_by_bit_query(oracle, n_bits):\n    result = 0\n    for i in range(n_bits):\n        if oracle(1 << i):\n            result |= (1 << i)\n    return result", BERNSTEIN_VAZIRANI),

    # SWAP -> QUANTUM SWAP
    ("def swap(a, b):\n    temp = a\n    a = b\n    b = temp\n    return a, b", QUANTUM_SWAP),
    ("a, b = b, a", QUANTUM_SWAP),
    ("def exchange(x, y):\n    x, y = y, x\n    return x, y", QUANTUM_SWAP),

    # SEND STATE -> TELEPORTATION
    ("def send_message(state, channel):\n    channel.write(state)\n    return state", TELEPORTATION),
    ("def transmit(data, receiver):\n    receiver.receive(data)\n    return True", TELEPORTATION),
    ("def copy_state(src, dst):\n    dst = src\n    return dst", TELEPORTATION),
]

# ============================================================
# VARIATION TRANSFORMS
# ============================================================

PARAM_POOLS = {
    "lst":    ["arr", "array", "data", "sequence", "haystack", "collection", "elements"],
    "target": ["key", "query", "needle", "value", "search_val", "wanted"],
    "items":  ["data", "arr", "seq", "elements", "collection"],
    "arr":    ["lst", "data", "sequence", "items", "nums"],
    "index":  ["idx", "pos", "position"],
    "val":    ["elem", "v", "item", "current", "entry"],
    "i":      ["idx", "pos", "k"],
    "x":      ["key", "target", "needle", "query"],
    "n":      ["size", "length", "num_bits"],
    "a":      ["p", "first", "val1"],
    "b":      ["q", "second", "val2"],
    "f":      ["func", "oracle", "fn", "callback"],
    "func":   ["oracle", "fn", "predicate"],
}

DOCSTRINGS = [
    '    """Search for target in list."""',
    '    """Linear scan implementation."""',
    '    """Returns index if found, else -1."""',
    '    """Naive sequential search. O(N) time."""',
    '    """Iterate and compare each element."""',
    '    """Classic brute-force search."""',
    '    """Check every element sequentially."""',
    '    """Unstructured search, no sorting required."""',
]

INLINE_COMMENTS = [
    "  # check each element",
    "  # sequential scan",
    "  # compare values",
    "  # O(N) operation",
    "  # linear pass",
    "  # scan forward",
]

NOISE_VARS = [
    "    found = False",
    "    count = 0",
    "    result = None",
    "    step = 1",
    "    checked = 0",
    "    iterations = 0",
]

CLASS_NAMES = ["Searcher", "Solver", "Processor", "Algorithm", "Handler", "Scanner", "Finder"]

TYPE_HINT_MAP = [
    (r'\(lst\b',        '(lst: list'),
    (r'\(arr\b',        '(arr: list'),
    (r',\s*target\b',   ', target: int'),
    (r'\(target\b',     '(target: int'),
    (r',\s*n\b\)',      ', n: int)'),
    (r'\(f\b',          '(f: callable'),
    (r'\(func\b',       '(func: callable'),
]


def rename_params(code):
    for original, pool in PARAM_POOLS.items():
        pattern = r'\b' + re.escape(original) + r'\b'
        if re.search(pattern, code) and random.random() < 0.55:
            code = re.sub(pattern, random.choice(pool), code)
    return code


def add_docstring(code):
    lines = code.splitlines()
    out = []
    for line in lines:
        out.append(line)
        if re.match(r'\s*def \w+\(.*\)\s*:', line):
            out.append(random.choice(DOCSTRINGS))
    return "\n".join(out)


def sprinkle_comments(code):
    lines = code.splitlines()
    out = []
    for line in lines:
        if line.strip() and not line.strip().startswith("#") and random.random() < 0.25:
            line += random.choice(INLINE_COMMENTS)
        out.append(line)
    return "\n".join(out)


def add_type_hints(code):
    for pattern, replacement in TYPE_HINT_MAP:
        if random.random() < 0.4:
            code = re.sub(pattern, replacement, code, count=1)
    return code


def inject_noise_var(code):
    lines = code.splitlines()
    out = []
    done = False
    for line in lines:
        out.append(line)
        if not done and re.match(r'\s*def \w+\(.*\)\s*:', line):
            out.append(random.choice(NOISE_VARS))
            done = True
    return "\n".join(out)


def wrap_in_class(code):
    if not code.strip().startswith("def "):
        return code
    name = random.choice(CLASS_NAMES)
    indented = "\n".join("    " + l for l in code.splitlines())
    return f"class {name}:\n{indented}"


def for_to_while(code):
    m = re.search(r'for (\w+) in range\(len\((\w+)\)\):', code)
    if m:
        idx, col = m.group(1), m.group(2)
        indent = re.search(r'(\s*)for', code).group(1)
        code = re.sub(
            r'for \w+ in range\(len\(\w+\)\):',
            f"{idx} = 0\n{indent}while {idx} < len({col}):",
            code, count=1
        )
        # Add increment at end of while body (after last line of loop)
        code = code.rstrip() + f"\n{indent}    {idx} += 1"
    return code


def early_exit_rewrite(code):
    # Rewrite "if val == target: return i" as continue-on-mismatch
    code = re.sub(
        r'if (\w+) == (\w+):\s*\n(\s*)return (\w+)',
        r'if \1 != \2:\n\3    continue\n\3return \4',
        code
    )
    return code


def functional_rewrite(code):
    if re.search(r'def \w+\(\w+,\s*\w+\)', code) and 'enumerate' in code:
        params = re.search(r'def \w+\((\w+),\s*(\w+)\)', code)
        if params:
            col, tgt = params.group(1), params.group(2)
            fname = re.search(r'def (\w+)', code).group(1)
            return (
                f"def {fname}({col}, {tgt}):\n"
                f"    return next(\n"
                f"        (i for i, v in enumerate({col}) if v == {tgt}),\n"
                f"        -1\n"
                f"    )"
            )
    return code


def verbose_deutsch(code):
    if re.search(r'is_constant|check_function|two_query_check', code):
        names = ["evaluate_function", "classify_oracle", "determine_type", "probe_function"]
        fname = random.choice(names)
        arg = random.choice(["f", "func", "oracle", "fn"])
        return (
            f"def {fname}({arg}):\n"
            f"    output_at_zero = {arg}(0)\n"
            f"    output_at_one = {arg}(1)\n"
            f"    outputs_match = (output_at_zero == output_at_one)\n"
            f"    if outputs_match:\n"
            f"        classification = 'constant'\n"
            f"    else:\n"
            f"        classification = 'balanced'\n"
            f"    return classification"
        )
    return code


def xor_swap(code):
    if re.search(r'def swap|def exchange', code):
        params = re.search(r'def \w+\((\w+),\s*(\w+)\)', code)
        if params:
            a, b = params.group(1), params.group(2)
            fname = re.search(r'def (\w+)', code).group(1)
            return (
                f"def {fname}({a}, {b}):\n"
                f"    {a} = {a} ^ {b}\n"
                f"    {b} = {a} ^ {b}\n"
                f"    {a} = {a} ^ {b}\n"
                f"    return {a}, {b}"
            )
    return code


def rng_rewrite(code):
    if re.search(r'coin_flip|random_bit|flip_coin', code):
        rewrites = [
            "import random\ndef coin_flip():\n    return int(random.random() >= 0.5)",
            "import random\ndef sample_bit():\n    return random.choices([0, 1])[0]",
            "import random\ndef bernoulli_sample():\n    p = random.random()\n    return 1 if p > 0.5 else 0",
            "import random\ndef generate_bit():\n    bits = [0, 1]\n    random.shuffle(bits)\n    return bits[0]",
            "import random\ndef toss():\n    outcome = random.randint(0, 1)\n    return outcome",
            "import random\ndef draw_bit():\n    population = [0, 0, 1, 1]\n    return random.choice(population)",
        ]
        return random.choice(rewrites)
    return code


def verbose_teleport(code):
    if re.search(r'send_message|transmit|copy_state', code):
        templates = [
            "def transfer_state(source, destination):\n    data = source\n    if data is None:\n        raise ValueError('Nothing to send')\n    destination = data\n    return destination",
            "def relay(payload, sink):\n    if payload is not None:\n        sink = payload\n    return sink",
            "def forward(msg, target_node):\n    buffer = msg\n    target_node = buffer\n    success = True\n    return success",
        ]
        return random.choice(templates)
    return code


def verbose_bv(code):
    if re.search(r'find_secret|recover_bitstring|bit_by_bit_query', code):
        names = ["discover_hidden_string", "extract_secret", "query_oracle_bitwise", "decode_hidden_bits"]
        fname = random.choice(names)
        return (
            f"def {fname}(oracle, num_bits):\n"
            f"    hidden = []\n"
            f"    for position in range(num_bits):\n"
            f"        probe = [0] * num_bits\n"
            f"        probe[position] = 1\n"
            f"        response = oracle(probe)\n"
            f"        hidden.append(response)\n"
            f"    return ''.join(str(b) for b in hidden)"
        )
    return code


def prefix_comment(code):
    prefixes = [
        "# Classical implementation\n",
        "# Python version\n",
        "# Naive approach\n",
        "# Standard solution\n",
        "# Brute force\n",
        "# Sequential method\n",
    ]
    return random.choice(prefixes) + code


TRANSFORMS = [
    rename_params,
    add_docstring,
    sprinkle_comments,
    add_type_hints,
    inject_noise_var,
    wrap_in_class,
    for_to_while,
    early_exit_rewrite,
    functional_rewrite,
    verbose_deutsch,
    xor_swap,
    rng_rewrite,
    verbose_teleport,
    verbose_bv,
    prefix_comment,
]


def make_variation(py):
    """Apply 1–4 randomly chosen transforms. Never crash."""
    n = random.randint(1, 4)
    chosen = random.sample(TRANSFORMS, min(n, len(TRANSFORMS)))
    result = py
    for t in chosen:
        try:
            candidate = t(result)
            if candidate and candidate.strip():
                result = candidate
        except Exception:
            pass
    return result


# ============================================================
# BUILD POOL
# ============================================================
pool = []
for py, q in base_pairs:
    pool.append((py, q))
    for _ in range(14):
        varied = make_variation(py)
        if varied.strip() != py.strip():
            pool.append((varied, q))

print(f"Variation pool size: {len(pool)}")

# ============================================================
# WRITE JSONL
# ============================================================
with OUT.open("w") as f:
    for _ in range(1500):
        py, q = random.choice(pool)
        f.write(json.dumps({
            "input": "Translate Python to quantum circuit:\n" + py,
            "output": q
        }) + "\n")

print("✅ Enhanced quantum dataset written")
print(f"   Output  : {OUT}")
print(f"   Examples: 350")
print()
print("Algorithms  :  Classical  →  Quantum")
print("  1. Linear Search         →  Grover's Algorithm")
print("  2. Coin Flip / RNG       →  Hadamard Randomness")
print("  3. Function Parity Check →  Deutsch's Algorithm")
print("  4. Hidden Bitstring      →  Bernstein-Vazirani")
print("  5. Variable Swap         →  Quantum SWAP (3 CNOTs)")
print("  6. Send / Copy State     →  Quantum Teleportation")
print()
print("Transforms applied per example (1-4 randomly):")
print("  rename_params, add_docstring, sprinkle_comments,")
print("  add_type_hints, inject_noise_var, wrap_in_class,")
print("  for_to_while, early_exit_rewrite, functional_rewrite,")
print("  verbose_deutsch, xor_swap, rng_rewrite,")
print("  verbose_teleport, verbose_bv, prefix_comment")