import json
import random
import re
from pathlib import Path

OUT = Path("better_datasets/python_to_quantum5.jsonl")
OUT.parent.mkdir(exist_ok=True)

# ============================================================
# QUANTUM CIRCUIT TARGETS
# ============================================================

SHOR = (
    "# Shor's algorithm: 15 = 3 × 5 (factoring 15 using 2 qubits for illustration)\n"
    "qc = QuantumCircuit(5, 3)\n"
    "qc.x(4)\n"
    "qc.h([0, 1, 2])\n"
    "qc.barrier()\n"
    "qc.cx(0, 3)\n"
    "qc.cx(1, 3)\n"
    "qc.cx(2, 3)\n"
    "qc.barrier()\n"
    "qc.h([0, 1, 2])\n"
    "qc.measure([0, 1, 2], [0, 1, 2])"
)

AMPLITUDE_AMPLIFICATION = (
    "# Amplitude amplification: search for |11⟩ state\n"
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

QUANTUM_FOURIER = (
    "# QFT: period finding (2-qubit QFT example)\n"
    "qc = QuantumCircuit(2, 2)\n"
    "qc.h(0)\n"
    "qc.cp(3.14159/2, 0, 1)\n"
    "qc.h(1)\n"
    "qc.swap(0, 1)\n"
    "qc.measure([0, 1], [0, 1])"
)

QUANTUM_WALK = (
    "# Quantum walk on line (1D)\n"
    "qc = QuantumCircuit(3, 3)\n"
    "qc.h(0)\n"
    "qc.x(1)\n"
    "qc.h(1)\n"
    "qc.cx(0, 2)\n"
    "qc.cx(1, 2)\n"
    "qc.h(0)\n"
    "qc.measure([0, 1, 2], [0, 1, 2])"
)

# ============================================================
# BASE EXAMPLES
# ============================================================

base_pairs = [
    # FACTORING -> SHOR
    ("def factor(n):\n    for i in range(2, n):\n        if n % i == 0:\n            return i, n // i\n    return None", SHOR),
    ("def find_factors(number):\n    for divisor in range(2, number):\n        if number % divisor == 0:\n            return divisor, number // divisor\n    return None", SHOR),
    ("def factorize(n):\n    for i in range(2, int(n**0.5)+1):\n        if n % i == 0:\n            return i, n//i\n    return None", SHOR),

    # DATABASE SEARCH -> AMPLITUDE AMPLIFICATION
    ("def search(lst, condition):\n    for i, v in enumerate(lst):\n        if condition(v):\n            return i\n    return -1", AMPLITUDE_AMPLIFICATION),
    ("def find_matching(data, predicate):\n    for idx, item in enumerate(data):\n        if predicate(item):\n            return idx\n    return -1", AMPLITUDE_AMPLIFICATION),
    ("def locate_element(array, test_fn):\n    for pos in range(len(array)):\n        if test_fn(array[pos]):\n            return pos\n    return -1", AMPLITUDE_AMPLIFICATION),

    # PERIOD FINDING -> QUANTUM FOURIER TRANSFORM
    ("def find_period(f, limit):\n    first = f(0)\n    for r in range(1, limit):\n        if f(r) == first:\n            return r\n    return None", QUANTUM_FOURIER),
    ("def get_period(func, max_steps):\n    first_val = func(0)\n    for step in range(1, max_steps):\n        if func(step) == first_val:\n            return step\n    return None", QUANTUM_FOURIER),
    ("def detect_cycle(func, bound):\n    start = func(0)\n    for k in range(1, bound):\n        if func(k) == start:\n            return k\n    return -1", QUANTUM_FOURIER),

    # RANDOM WALK -> QUANTUM WALK
    ("def random_walk(position):\n    import random\n    step = random.choice([-1, 1])\n    return position + step", QUANTUM_WALK),
    ("def walk(pos):\n    from random import randint\n    direction = -1 if randint(0,1) == 0 else 1\n    return pos + direction", QUANTUM_WALK),
    ("def stochastic_move(location):\n    import random as r\n    displacement = r.choice([-1, 0, 1])\n    return location + displacement", QUANTUM_WALK),
]

# ============================================================
# VARIATION TRANSFORMS
# ============================================================

PARAM_POOLS = {
    "n":      ["number", "num", "value", "target", "N", "integer"],
    "number": ["n", "val", "input_num", "candidate"],
    "i":      ["j", "divisor", "candidate", "factor_candidate"],
    "lst":    ["arr", "array", "data", "sequence", "haystack", "collection"],
    "condition": ["predicate", "func", "test", "filter_fn", "criteria"],
    "v":      ["val", "item", "element", "current"],
    "f":      ["func", "function", "oracle", "mapping"],
    "limit":  ["max_steps", "bound", "max_iter", "upper_bound"],
    "r":      ["period", "shift", "step", "k"],
    "position": ["pos", "location", "coord", "spot"],
}

DOCSTRINGS = [
    '    """Find non-trivial factors of n."""',
    '    """Search for element satisfying condition."""',
    '    """Locate first matching element."""',
    '    """Discover period of function f."""',
    '    """Classical factoring algorithm. O(sqrt(n)) naive."""',
    '    """Sequential search with predicate."""',
    '    """Period detection by brute force."""',
    '    """Simulate one step of random walk."""',
    '    """Simple one-dimensional random walk."""',
]

INLINE_COMMENTS = [
    "  # trial division",
    "  # check each divisor",
    "  # test condition",
    "  # linear scan",
    "  # compare values",
    "  # found match",
    "  # take random step",
    "  # move left or right",
]

NOISE_VARS = [
    "    found = False",
    "    count = 0",
    "    result = None",
    "    step = 1",
    "    checked = 0",
    "    iterations = 0",
    "    temp = None",
]

CLASS_NAMES = ["Factorizer", "Searcher", "PeriodFinder", "Walker", "Algorithm", "Solver"]

TYPE_HINT_MAP = [
    (r'\(n\b',        '(n: int'),
    (r'\(number\b',   '(number: int'),
    (r',\s*condition\b',   ', condition: callable'),
    (r',\s*predicate\b',   ', predicate: callable'),
    (r'\(f\b',        '(f: callable'),
    (r'\(func\b',     '(func: callable'),
    (r',\s*limit\b\)', ', limit: int)'),
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
    """
    Wraps a standalone function in a class. Applied last in the pipeline
    to avoid breaking regex-based transforms. Inserts 'self' as the first
    parameter of every method so the output is valid Python.
    """
    if not re.search(r'^\s*def \w+', code, re.MULTILINE):
        return code
    if code.strip().startswith("class "):
        return code
    name = random.choice(CLASS_NAMES)
    indented = "\n".join("    " + l for l in code.splitlines())
    # FIX: insert 'self' as first param so class methods are valid Python
    indented = re.sub(r'(    def \w+\()', r'\1self, ', indented)
    # Clean up zero-arg edge case: (self, ) → (self)
    indented = indented.replace("(self, )", "(self)")
    return f"class {name}:\n{indented}"


def for_to_while(code):
    """
    Converts for/range loops to while loops, placing the increment
    correctly inside the loop body rather than at the end of the function.
    """
    patterns = [
        (r'for (\w+) in range\((\w+)\):', '{idx} = 0', 'while {idx} < {col}:'),
        (r'for (\w+) in range\(2, (\w+)\):', '{idx} = 2', 'while {idx} < {col}:'),
        (r'for (\w+) in range\(1, (\w+)\):', '{idx} = 1', 'while {idx} < {col}:'),
        (r'for (\w+) in range\(len\((\w+)\)\):', '{idx} = 0', 'while {idx} < len({col}):'),
    ]
    lines = code.splitlines()
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        matched = False
        for pattern, init_tmpl, while_tmpl in patterns:
            m = re.match(r'(\s*)' + pattern, line)
            if m:
                indent = m.group(1)
                idx = m.group(2)
                col = m.group(3)
                result.append(indent + init_tmpl.format(idx=idx, col=col))
                result.append(indent + while_tmpl.format(idx=idx, col=col))
                i += 1
                body = []
                while i < len(lines):
                    body_line = lines[i]
                    if body_line.strip() == '' or len(body_line) - len(body_line.lstrip()) > len(indent):
                        body.append(body_line)
                        i += 1
                    else:
                        break
                result.extend(body)
                result.append(indent + "    " + f"{idx} += 1")
                matched = True
                break
        if not matched:
            result.append(line)
            i += 1
    return "\n".join(result)


def early_exit_rewrite(code):
    """
    Rewrites early-return patterns to continue-based loops.
    Back-references preserve original return order (no swapping).
    """
    if re.search(r'if \w+ % \w+ == 0', code):
        code = re.sub(
            r'if (\w+) % (\w+) == 0:\s*\n(\s*)return (\w+), (\w+) // (\w+)',
            r'if \1 % \2 != 0:\n\3    continue\n\3return \4, \5 // \6',
            code
        )
    elif re.search(r'if \w+\(\w+\)', code):
        code = re.sub(
            r'if (\w+)\((\w+)\):\s*\n(\s*)return (\w+)',
            r'if not \1(\2):\n\3    continue\n\3return \4',
            code
        )
    return code


def verbose_factoring(code):
    if re.search(r'factor|factorize', code):
        names = ["trial_division", "find_prime_factors", "decompose_integer", "factorization"]
        fname = random.choice(names)
        return (
            f"def {fname}(candidate):\n"
            f"    if candidate < 2:\n"
            f"        return None\n"
            f"    for potential_divisor in range(2, int(candidate**0.5) + 1):\n"
            f"        if candidate % potential_divisor == 0:\n"
            f"            quotient = candidate // potential_divisor\n"
            f"            return (potential_divisor, quotient)\n"
            f"    return None  # candidate is prime"
        )
    return code


def enumerate_rewrite(code):
    """
    Rewrites search functions as a single next() expression.
    Matches both enumerate() and range(len()) based loops.
    """
    if not re.search(r'search|locate_element|find_matching', code):
        return code
    params = re.search(r'def (\w+)\((\w+),\s*(\w+)\)', code)
    if not params:
        return code
    fname, col, tgt = params.group(1), params.group(2), params.group(3)
    return (
        f"def {fname}({col}, {tgt}):\n"
        f"    return next(\n"
        f"        (i for i, v in enumerate({col}) if {tgt}(v)),\n"
        f"        -1\n"
        f"    )"
    )


def period_verbose(code):
    if re.search(r'find_period|get_period|detect_cycle', code):
        names = ["discover_period", "find_repetition", "compute_cycle_length"]
        fname = random.choice(names)
        return (
            f"def {fname}(function, max_iterations):\n"
            f"    reference_value = function(0)\n"
            f"    for step_count in range(1, max_iterations):\n"
            f"        current_value = function(step_count)\n"
            f"        if current_value == reference_value:\n"
            f"            return step_count\n"
            f"    return None  # period not found"
        )
    return code


def walk_rewrite(code):
    if re.search(r'random_walk|walk|stochastic_move', code):
        templates = [
            "import random\ndef walk_one_step(location):\n    direction = random.choice([-1, 1])\n    return location + direction",
            "import random as r\ndef move(position):\n    step = r.choice([-1, 0, 1])\n    return position + step",
            "from random import randint\ndef advance(pos):\n    return pos + (1 if randint(0,1) else -1)",
        ]
        return random.choice(templates)
    return code


def prefix_comment(code):
    prefixes = [
        "# Classical factoring\n",
        "# Naive search\n",
        "# Brute force period finding\n",
        "# Classical random walk\n",
        "# Deterministic approach\n",
        "# Pre-quantum algorithm\n",
    ]
    return random.choice(prefixes) + code


# wrap_in_class is intentionally excluded from TRANSFORMS and applied separately
# at the end of make_variation to avoid breaking regex-based transforms.
TRANSFORMS = [
    rename_params,
    add_docstring,
    sprinkle_comments,
    add_type_hints,
    inject_noise_var,
    for_to_while,
    early_exit_rewrite,
    enumerate_rewrite,
    verbose_factoring,
    period_verbose,
    walk_rewrite,
    prefix_comment,
]


def make_variation(py):
    """
    Apply 1–4 randomly chosen transforms, then optionally wrap in a class.
    wrap_in_class is always applied last to avoid breaking earlier regex transforms.
    """
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
    # Optionally wrap in class last, after all other transforms
    if random.random() < 0.15:
        try:
            result = wrap_in_class(result)
        except Exception:
            pass
    return result


# ============================================================
# BUILD POOL  (with deduplication)
# ============================================================
seen = set()
pool = []

def add_to_pool(py, q):
    key = (py.strip(), q.strip())
    if key not in seen:
        seen.add(key)
        pool.append((py, q))

for py, q in base_pairs:
    add_to_pool(py, q)
    for _ in range(14):
        varied = make_variation(py)
        if varied.strip() != py.strip():
            add_to_pool(varied, q)

print(f"Variation pool size: {len(pool)}")

# ============================================================
# WRITE JSONL
# ============================================================
NUM_EXAMPLES = 1500

with OUT.open("w") as f:
    for _ in range(NUM_EXAMPLES):
        py, q = random.choice(pool)
        f.write(json.dumps({
            "input": "Translate Python to quantum circuit:\n" + py,
            "output": q
        }) + "\n")

print("✅ Enhanced quantum dataset written")
print(f"   Output  : {OUT}")
print(f"   Examples: {NUM_EXAMPLES}")
print()
print("Algorithms  :  Classical  →  Quantum")
print("  1. Factoring (trial division)  →  Shor's Algorithm")
print("  2. Database Search              →  Amplitude Amplification")
print("  3. Period Finding               →  Quantum Fourier Transform")
print("  4. Random Walk                  →  Quantum Walk")
print()
print("Transforms applied per example (1-4 randomly, class wrap always last):")
print("  rename_params, add_docstring, sprinkle_comments,")
print("  add_type_hints, inject_noise_var, wrap_in_class,")
print("  for_to_while, early_exit_rewrite, enumerate_rewrite,")
print("  verbose_factoring, period_verbose, walk_rewrite,")
print("  prefix_comment")