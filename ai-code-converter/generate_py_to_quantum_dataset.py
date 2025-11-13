import random
import json
import textwrap

# ----------------------------------------
# Classical Code Generators
# ----------------------------------------

def generate_classical_not_code():
    var_name = random.choice(["x", "bit", "flag", "val"])
    return textwrap.dedent(f"""
    def classical_not({var_name}):
        return not {var_name}
    """)

def generate_classical_and_code():
    a, b = random.sample(["a", "b", "x", "y", "bit1", "bit2"], 2)
    return textwrap.dedent(f"""
    def classical_and({a}, {b}):
        return {a} and {b}
    """)

def generate_classical_or_code():
    a, b = random.sample(["a", "b", "x", "y", "bit1", "bit2"], 2)
    return textwrap.dedent(f"""
    def classical_or({a}, {b}):
        return {a} or {b}
    """)

def generate_classical_xor_code():
    a, b = random.sample(["a", "b", "x", "y", "bit1", "bit2"], 2)
    return textwrap.dedent(f"""
    def classical_xor({a}, {b}):
        return ({a} and not {b}) or (not {a} and {b})
    """)

# ----------------------------------------
# Quantum Code Generators (Qiskit)
# ----------------------------------------

def generate_quantum_not_code():
    return textwrap.dedent("""
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(1)
    qc.x(0)  # Quantum NOT gate
    qc.measure_all()
    """)

def generate_quantum_and_code():
    return textwrap.dedent("""
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(3)  # two inputs + one output
    qc.ccx(0, 1, 2)  # Toffoli gate acts as AND
    qc.measure_all()
    """)

def generate_quantum_or_code():
    return textwrap.dedent("""
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(3)
    # OR implemented using De Morgan’s law: OR = NOT(AND(NOT A, NOT B))
    qc.x([0, 1])       # NOT on inputs
    qc.ccx(0, 1, 2)    # AND
    qc.x(2)            # Final NOT
    qc.measure_all()
    """)

def generate_quantum_xor_code():
    return textwrap.dedent("""
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(3)
    qc.cx(0, 2)  # Copy input 1 to output
    qc.cx(1, 2)  # XOR operation
    qc.measure_all()
    """)

# ----------------------------------------
# Dataset Generation Logic
# ----------------------------------------

CLASSICAL_GENERATORS = [
    ("NOT", generate_classical_not_code, generate_quantum_not_code),
    ("AND", generate_classical_and_code, generate_quantum_and_code),
    ("OR", generate_classical_or_code, generate_quantum_or_code),
    ("XOR", generate_classical_xor_code, generate_quantum_xor_code)
]

def generate_dataset(n_samples_per_type=250):
    dataset = []
    for name, classical_gen, quantum_gen in CLASSICAL_GENERATORS:
        for _ in range(n_samples_per_type):
            dataset.append({
                "task": name,
                "input": classical_gen().strip(),
                "output": quantum_gen().strip()
            })
    random.shuffle(dataset)
    return dataset

# ----------------------------------------
# Main Execution
# ----------------------------------------

if __name__ == "__main__":
    dataset = generate_dataset(n_samples_per_type=250)
    
    with open("python_to_quantum_dataset.json", "w") as f:
        json.dump(dataset, f, indent=2)
    
    print(f"✅ Generated {len(dataset)} code pairs and saved to python_to_quantum_dataset.json")
