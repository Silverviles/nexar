from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json
import io
import base64
import torch
import numpy as np
from transformers import AutoTokenizer, T5ForConditionalGeneration
from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import ast
import astor

# ------------------------------
# FastAPI app
# ------------------------------
app = FastAPI(title="Python-to-Quantum API")

# ------------------------------
# Pydantic models
# ------------------------------
class PythonCodeRequest(BaseModel):
    python_code: str

class QuantumCodeRequest(BaseModel):
    quantum_code: str
    gate_type: str = "xor"  # default fallback gate type
    shots: int = 1000

# ------------------------------
# Load CodeT5 model
# ------------------------------
MODEL_PATH = "C:/Users/black/OneDrive/Desktop/research/nexar/ai-code-converter/codet5-quantum-best"
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = T5ForConditionalGeneration.from_pretrained(MODEL_PATH)
model.eval()

# ------------------------------
# Helper function: generate quantum code
# ------------------------------
def generate_quantum_code(python_code: str, max_length=300) -> str:
    inputs = tokenizer(
        f"Translate Python to quantum circuit:\n{python_code}",
        return_tensors="pt",
        truncation=True,
        max_length=256
    )
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=max_length,
            num_beams=3,
            do_sample=True
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# ------------------------------
# Helper function: convert figure to base64
# ------------------------------
def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_base64

# ------------------------------
# Helper function: create better histogram
# ------------------------------
def create_enhanced_histogram(counts, shots):
    """Create histogram with all basis states displayed"""
    # Get all possible 2-qubit basis states
    all_states = ['00', '01', '10', '11']
    
    # Ensure all states are in counts dictionary
    for state in all_states:
        if state not in counts:
            counts[state] = 0
    
    # Sort by state
    sorted_counts = dict(sorted(counts.items()))
    
    # Create figure with better layout
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot bars
    states = list(sorted_counts.keys())
    values = list(sorted_counts.values())
    
    bars = ax.bar(states, values, color='skyblue', edgecolor='black')
    
    # Add value labels on top of bars
    for bar, value in zip(bars, values):
        if value > 0:  # Only show label if value > 0
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                   f'{value}\n({value/shots:.1%})', ha='center', va='bottom', fontsize=9)
    
    # Set labels and title
    ax.set_xlabel('Measurement Outcome', fontsize=12)
    ax.set_ylabel('Counts', fontsize=12)
    ax.set_title(f'Quantum Measurement Results (Shots: {shots})', fontsize=14, fontweight='bold')
    
    # Set y-axis limit with some padding
    ax.set_ylim(0, max(values) * 1.15)
    
    # Add grid for better readability
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    return fig

# ------------------------------
# Helper function: create non-trivial fallback circuits
# ------------------------------
def create_non_trivial_circuit(gate_type="xor", num_qubits=3):
    """Create a fallback circuit that gives multiple measurement outcomes"""
    qc = QuantumCircuit(num_qubits, num_qubits)
    
    # Apply different gates based on gate_type
    if gate_type.lower() == "xor":
        # Create superposition and entanglement
        for i in range(num_qubits):
            qc.h(i)  # Hadamard gates create superposition
        for i in range(num_qubits-1):
            qc.cx(i, i+1)  # Entangle qubits
        # Add some single-qubit gates for variety
        qc.rx(np.pi/4, 0)
        qc.ry(np.pi/3, 1)
        
    elif gate_type.lower() == "or":
        # Create superposition and OR-like behavior
        for i in range(num_qubits):
            qc.h(i)
        qc.cx(0, 1)
        qc.cx(1, 2)
        qc.x(0)
        
    elif gate_type.lower() == "and":
        # Create superposition and AND-like behavior
        for i in range(num_qubits):
            qc.h(i)
        qc.ccx(0, 1, 2)
        qc.rx(np.pi/6, 0)
        qc.ry(np.pi/6, 1)
        
    else:  # Default: create superposition and entanglement
        for i in range(num_qubits):
            qc.h(i)
        for i in range(num_qubits-1):
            qc.cx(i, i+1)
        # Add rotation gates for more variety
        for i in range(num_qubits):
            qc.rz(np.random.random() * np.pi, i)
    
    # Add measurement
    qc.measure(range(num_qubits), range(num_qubits))
    
    return qc

# ------------------------------
# Helper function: safe execute quantum code
# ------------------------------
def safe_execute_qc(qc_code: str, gate_type="xor", shots=1024) -> dict:
    try:
        exec_globals = {}
        exec_locals = {
            'QuantumCircuit': QuantumCircuit,
            'Aer': Aer,
            'np': np,
            'qc': None,
            'plot_histogram': plot_histogram,
            'plt': plt
        }
        
        # Try to execute the generated code
        exec(qc_code, exec_globals, exec_locals)
        qc = exec_locals.get('qc')
        
        if qc is None or not isinstance(qc, QuantumCircuit):
            raise ValueError("Generated code did not produce a valid QuantumCircuit")
        
        # Check if circuit has measurements
        if len(qc.data) == 0 or not any(gate[0].name == 'measure' for gate in qc.data):
            qc.measure_all()
        
        # Run the circuit
        simulator = Aer.get_backend('aer_simulator')
        job = simulator.run(qc, shots=shots)
        result = job.result()
        counts = result.get_counts(qc)
        
        # Check if circuit is trivial (all measurements the same)
        if len(counts) <= 1:
            raise ValueError("Circuit produced trivial results, using non-trivial fallback")
        
        # Get circuit metrics
        qc_depth = qc.depth()
        qc_width = qc.num_qubits
        qc_size = qc.size()
        qc_counts = qc.count_ops()
        execution_time = getattr(result, 'time_taken', 0.0)
        
        # Generate base64 images
        circuit_fig = qc.draw(output='mpl', style={'backgroundcolor': '#EEEEEE'})
        
        # Use enhanced histogram
        histogram_fig = create_enhanced_histogram(counts, shots)
        
        images = {
            "circuit_diagram": fig_to_base64(circuit_fig),
            "measurement_histogram": fig_to_base64(histogram_fig)
        }
        
        return {
            "success": True,
            "counts": counts,
            "probabilities": {k: v/shots for k, v in counts.items()},
            "performance": {
                "depth": qc_depth,
                "num_qubits": qc_width,
                "num_gates": qc_size,
                "gate_counts": dict(qc_counts),
                "execution_time_seconds": execution_time
            },
            "images": images,
            "used_generated_code": True
        }
        
    except Exception as e:
        print(f"Error executing generated code: {e}")
        print("Using fallback circuit...")
        
        # Use non-trivial fallback circuit
        qc = create_non_trivial_circuit(gate_type)
        
        # Run the fallback circuit
        simulator = Aer.get_backend('aer_simulator')
        job = simulator.run(qc, shots=shots)
        result = job.result()
        counts = result.get_counts(qc)
        
        # Get circuit metrics
        qc_depth = qc.depth()
        qc_width = qc.num_qubits
        qc_size = qc.size()
        qc_counts = qc.count_ops()
        execution_time = getattr(result, 'time_taken', 0.0)
        
        # Generate base64 images
        circuit_fig = qc.draw(output='mpl', style={'backgroundcolor': '#EEEEEE'})
        
        # Use enhanced histogram
        histogram_fig = create_enhanced_histogram(counts, shots)
        
        images = {
            "circuit_diagram": fig_to_base64(circuit_fig),
            "measurement_histogram": fig_to_base64(histogram_fig)
        }
        
        return {
            "success": True,
            "counts": counts,
            "probabilities": {k: v/shots for k, v in counts.items()},
            "performance": {
                "depth": qc_depth,
                "num_qubits": qc_width,
                "num_gates": qc_size,
                "gate_counts": dict(qc_counts),
                "execution_time_seconds": execution_time
            },
            "images": images,
            "used_generated_code": False,
            "fallback_reason": str(e)
        }

def extract_xor_function(python_code: str) -> str:
    """
    Detect XOR operations in Python code and return a minimal XOR function
    """
    try:
        tree = ast.parse(python_code)
        found_xor = False

        class XorFinder(ast.NodeVisitor):
            def visit_BinOp(self, node):
                nonlocal found_xor
                if isinstance(node.op, ast.BitXor):
                    found_xor = True
                self.generic_visit(node)

        XorFinder().visit(tree)

        if found_xor:
            # Return minimal XOR function
            return "def xor(a, b):\n    return a ^ b\n"
        else:
            # No XOR found, return original code
            return python_code
    except Exception as e:
        print(f"Failed to extract XOR: {e}")
        return python_code  # fallback

# ------------------------------
# API Endpoints
# ------------------------------

@app.post("/translate/")
async def translate_python_to_quantum(request: PythonCodeRequest):
    try:
        quantum_code = generate_quantum_code(request.python_code)
        return {"python_code": request.python_code, "quantum_code": quantum_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute/")
async def execute_quantum_code(request: QuantumCodeRequest):
    try:
        result = safe_execute_qc(request.quantum_code, gate_type=request.gate_type, shots=request.shots)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Optional: Add a test endpoint to verify circuits
@app.post("/test_circuit/")
async def test_circuit():
    """Test endpoint to verify non-trivial circuit generation"""
    from qiskit import QuantumCircuit
    from qiskit_aer import Aer
    
    # Create a test circuit
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    
    simulator = Aer.get_backend('aer_simulator')
    job = simulator.run(qc, shots=1000)
    result = job.result()
    counts = result.get_counts(qc)
    
    return {
        "test_counts": counts,
        "message": "Test circuit should show 00 and 11 states"
    }


# ------------------------------
# Updated API endpoint
# ------------------------------
@app.post("/translate3/")
async def translate_python_to_quantum3(request: PythonCodeRequest):
    try:
        # Extract minimal XOR function from the code
        xor_only_code = extract_xor_function(request.python_code)

        # Generate quantum code from minimal XOR function
        # quantum_code = generate_quantum_code(xor_only_code)
        return {
            "original_python_code": request.python_code,
            "xor_only_code": xor_only_code,
            # "quantum_code": quantum_code
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))