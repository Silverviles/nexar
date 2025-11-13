"""
Dataset Collection and Management System
Creates structured format for Classical → Quantum code pairs
"""

import json
import os
from datetime import datetime

class DatasetManager:
    def __init__(self, dataset_dir="data"):
        self.dataset_dir = dataset_dir
        self.raw_dir = os.path.join(dataset_dir, "raw")
        self.processed_dir = os.path.join(dataset_dir, "processed")
        
        # Create directories
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        
        self.dataset_file = os.path.join(self.processed_dir, "code_pairs.json")
        self.load_dataset()
    
    def load_dataset(self):
        """Load existing dataset or create new one"""
        if os.path.exists(self.dataset_file):
            with open(self.dataset_file, 'r') as f:
                self.dataset = json.load(f)
        else:
            self.dataset = []
    
    def add_code_pair(self, classical_code, quantum_code, metadata):
        """
        Add a new classical-quantum code pair to dataset
        
        Args:
            classical_code (str): Classical Python code
            quantum_code (str): Equivalent Qiskit code
            metadata (dict): Additional information
        """
        entry = {
            "id": len(self.dataset) + 1,
            "timestamp": datetime.now().isoformat(),
            "classical_code": classical_code,
            "quantum_code": quantum_code,
            "metadata": metadata
        }
        
        self.dataset.append(entry)
        self.save_dataset()
        print(f"✅ Added pair #{entry['id']}: {metadata.get('algorithm_name', 'Unknown')}")
    
    def save_dataset(self):
        """Save dataset to JSON file"""
        with open(self.dataset_file, 'w') as f:
            json.dump(self.dataset, indent=2, fp=f)
    
    def get_stats(self):
        """Get dataset statistics"""
        if not self.dataset:
            return "Dataset is empty"
        
        categories = {}
        for entry in self.dataset:
            cat = entry['metadata'].get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total_pairs": len(self.dataset),
            "categories": categories
        }
    
    def export_for_training(self, output_file="training_data.json"):
        """Export in format suitable for CodeT5 training"""
        training_data = []
        for entry in self.dataset:
            training_data.append({
                "input": entry["classical_code"],
                "target": entry["quantum_code"],
                "metadata": entry["metadata"]
            })
        
        output_path = os.path.join(self.processed_dir, output_file)
        with open(output_path, 'w') as f:
            json.dump(training_data, indent=2, fp=f)
        
        print(f"✅ Exported {len(training_data)} pairs to {output_path}")


# ============================================================================
# STARTER EXAMPLES - Basic Algorithms
# ============================================================================

def create_starter_dataset():
    """Create initial dataset with basic algorithm examples"""
    dm = DatasetManager()
    
    # Example 1: Simple Addition
    dm.add_code_pair(
        classical_code="""# Classical: Add two numbers
def add_numbers(a, b):
    return a + b

result = add_numbers(3, 5)
print(result)  # Output: 8""",
        
        quantum_code="""# Quantum: Add two numbers using quantum gates
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def quantum_add(a, b):
    # Convert to binary (simplified for 3-bit numbers)
    qr = QuantumRegister(6, 'q')
    cr = ClassicalRegister(4, 'c')
    qc = QuantumCircuit(qr, cr)
    
    # Encode first number
    if a & 1: qc.x(0)
    if a & 2: qc.x(1)
    if a & 4: qc.x(2)
    
    # Encode second number
    if b & 1: qc.x(3)
    if b & 2: qc.x(4)
    if b & 4: qc.x(5)
    
    # Quantum adder circuit (simplified)
    qc.cx(3, 0)  # Add bits
    qc.cx(4, 1)
    qc.cx(5, 2)
    
    qc.measure([0,1,2,3], [0,1,2,3])
    return qc

circuit = quantum_add(3, 5)""",
        
        metadata={
            "algorithm_name": "addition",
            "category": "arithmetic",
            "difficulty": "basic",
            "input_size": "small",
            "quantum_advantage": "none",
            "description": "Simple addition operation"
        }
    )
    
    # Example 2: Boolean OR
    dm.add_code_pair(
        classical_code="""# Classical: Boolean OR operation
def boolean_or(a, b):
    return a or b

result = boolean_or(True, False)
print(result)  # Output: True""",
        
        quantum_code="""# Quantum: Boolean OR using quantum gates
from qiskit import QuantumCircuit

def quantum_or(a, b):
    qc = QuantumCircuit(3, 1)
    
    # Encode inputs
    if a: qc.x(0)
    if b: qc.x(1)
    
    # OR logic: output is 1 if either input is 1
    qc.x(0)  # NOT a
    qc.x(1)  # NOT b
    qc.ccx(0, 1, 2)  # Toffoli: output = (NOT a) AND (NOT b)
    qc.x(2)  # NOT output = OR(a, b)
    
    qc.measure(2, 0)
    return qc

circuit = quantum_or(True, False)""",
        
        metadata={
            "algorithm_name": "boolean_or",
            "category": "logic",
            "difficulty": "basic",
            "input_size": "small",
            "quantum_advantage": "none",
            "description": "Boolean OR operation using quantum gates"
        }
    )
    
    # Example 3: Find Maximum
    dm.add_code_pair(
        classical_code="""# Classical: Find maximum of two numbers
def find_max(a, b):
    if a > b:
        return a
    else:
        return b

result = find_max(7, 5)
print(result)  # Output: 7""",
        
        quantum_code="""# Quantum: Compare two numbers
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def quantum_compare(a, b, n_bits=3):
    qr = QuantumRegister(n_bits*2 + 1, 'q')
    cr = ClassicalRegister(1, 'c')
    qc = QuantumCircuit(qr, cr)
    
    # Encode first number in qubits 0 to n_bits-1
    for i in range(n_bits):
        if a & (1 << i):
            qc.x(i)
    
    # Encode second number in qubits n_bits to 2*n_bits-1
    for i in range(n_bits):
        if b & (1 << i):
            qc.x(n_bits + i)
    
    # Comparison circuit (simplified)
    # Result qubit will be 1 if a > b
    for i in range(n_bits):
        qc.cx(i, 2*n_bits)
        qc.x(n_bits + i)
        qc.ccx(n_bits + i, i, 2*n_bits)
        qc.x(n_bits + i)
    
    qc.measure(2*n_bits, 0)
    return qc

circuit = quantum_compare(7, 5)""",
        
        metadata={
            "algorithm_name": "find_maximum",
            "category": "comparison",
            "difficulty": "intermediate",
            "input_size": "small",
            "quantum_advantage": "none",
            "description": "Find maximum of two numbers"
        }
    )
    
    # Example 4: Linear Search (Simplified)
    dm.add_code_pair(
        classical_code="""# Classical: Linear search
def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1

arr = [2, 5, 7, 8]
result = linear_search(arr, 7)
print(result)  # Output: 2""",
        
        quantum_code="""# Quantum: Grover's search (simplified for small array)
from qiskit import QuantumCircuit
from qiskit.circuit.library import GroverOperator

def quantum_search(arr, target):
    n = 2  # For 4 items, we need 2 qubits
    qc = QuantumCircuit(n)
    
    # Initialize superposition
    qc.h(range(n))
    
    # Oracle: mark the target state
    # For target at index 2 (binary: 10)
    target_binary = format(arr.index(target), f'0{n}b')
    
    # Create oracle
    for i, bit in enumerate(target_binary):
        if bit == '0':
            qc.x(i)
    
    # Multi-controlled Z
    qc.h(n-1)
    qc.mcx(list(range(n-1)), n-1)
    qc.h(n-1)
    
    # Uncompute
    for i, bit in enumerate(target_binary):
        if bit == '0':
            qc.x(i)
    
    # Diffusion operator
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n-1)
    qc.mcx(list(range(n-1)), n-1)
    qc.h(n-1)
    qc.x(range(n))
    qc.h(range(n))
    
    qc.measure_all()
    return qc

circuit = quantum_search([2, 5, 7, 8], 7)""",
        
        metadata={
            "algorithm_name": "linear_search",
            "category": "search",
            "difficulty": "advanced",
            "input_size": "small",
            "quantum_advantage": "yes",
            "description": "Search using Grover's algorithm"
        }
    )
    
    print("\n" + "="*60)
    print("📊 DATASET STATISTICS")
    print("="*60)
    stats = dm.get_stats()
    print(f"Total pairs: {stats['total_pairs']}")
    print(f"Categories: {stats['categories']}")
    
    # Export for training
    dm.export_for_training()
    
    return dm


# ============================================================================
# TEMPLATE FOR ADDING NEW PAIRS
# ============================================================================

def add_new_pair_template():
    """Template function - copy this to add new algorithm pairs"""
    dm = DatasetManager()
    
    dm.add_code_pair(
        classical_code="""# Your classical Python code here
def algorithm_name():
    pass
""",
        
        quantum_code="""# Your Qiskit quantum code here
from qiskit import QuantumCircuit

def quantum_algorithm_name():
    qc = QuantumCircuit(2)
    # Add gates here
    return qc
""",
        
        metadata={
            "algorithm_name": "your_algorithm",
            "category": "arithmetic/logic/search/sorting/optimization",
            "difficulty": "basic/intermediate/advanced",
            "input_size": "small/medium/large",
            "quantum_advantage": "yes/no/potential",
            "description": "Brief description of the algorithm"
        }
    )


if __name__ == "__main__":
    print("🚀 Creating Starter Dataset...")
    print("="*60)
    
    dm = create_starter_dataset()
    
    print("\n✅ Dataset created successfully!")
    print(f"📁 Location: {dm.dataset_file}")
   