from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
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
import re

app = FastAPI(title="Python-Search-to-Quantum API")

class SearchAlgorithmRequest(BaseModel):
    python_code: str
    gate_type: str = "xor"  # xor, or, and, not, nor
    shots: int = 1024
    max_length: int = 300

MODEL_PATH = "C:/Users/black/OneDrive/Desktop/research/nexar/ai-code-converter/codet5-quantum-best"
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = T5ForConditionalGeneration.from_pretrained(MODEL_PATH)
model.eval()

def generate_quantum_code(python_code: str, max_length=300) -> str:
    """Generate quantum code using the CodeT5 model"""
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


def extract_gate_function(python_code: str, gate_type: str) -> str:
    """
    Extract the specific gate function from Python code based on gate_type.
    Improved to handle any function name containing the gate type.
    """
    gate_type = gate_type.lower()
    
    gate_patterns = {
        "xor": [
            r'def\s+\w*xor\w*\([^)]+\):[^}]*return[^}]*\^',   
            r'def\s+\w+\([^)]+\):[^}]*return[^}]*\^',         
            r'return\s+[a-zA-Z_]\w*\s*\^\s*[a-zA-Z_]\w*',    
            r'[a-zA-Z_]\w*\s*\^\s*[a-zA-Z_]\w*',             
        ],
        "or": [
            r'def\s+\w*or\w*\([^)]+\):[^}]*return[^}]*\|',
            r'def\s+\w+\([^)]+\):[^}]*return[^}]*\|',
            r'return\s+[a-zA-Z_]\w*\s*\|\s*[a-zA-Z_]\w*',
            r'[a-zA-Z_]\w*\s*or\s*[a-zA-Z_]\w*',
        ],
        "and": [
            r'def\s+\w*and\w*\([^)]+\):[^}]*return[^}]*\&',
            r'def\s+\w+\([^)]+\):[^}]*return[^}]*\&',
            r'return\s+[a-zA-Z_]\w*\s*\&\s*[a-zA-Z_]\w*',
            r'[a-zA-Z_]\w*\s*and\s*[a-zA-Z_]\w*',
        ],
        "not": [
            r'def\s+\w*not\w*\([^)]+\):[^}]*return[^}]*not',
            r'def\s+\w+\([^)]+\):[^}]*return[^}]*~',
            r'return\s+not\s+[a-zA-Z_]\w*',
            r'~\s*[a-zA-Z_]\w*',
        ],
        "nor": [
            r'def\s+\w*nor\w*\([^)]+\):[^}]*return[^}]*not.*or',
            r'return\s+not\s*\([^)]*\|\|[^)]*\)',
            r'not\s*\([^)]*or[^)]*\)',
        ]
    }
    
    patterns = gate_patterns.get(gate_type, gate_patterns["xor"])
    
    for pattern in patterns:
        matches = re.findall(pattern, python_code, re.DOTALL | re.IGNORECASE)
        if matches:
            for match in matches:
                lines = python_code.split('\n')
                for i, line in enumerate(lines):
                    if match in line or (gate_type in line.lower() and 'def' in line):
                        func_start = i
                        for j in range(i, len(lines)):
                            if lines[j].strip() == '' and j > i:
                                func_end = j
                                return '\n'.join(lines[func_start:func_end])
                        return '\n'.join(lines[func_start:])
    
    raise RuntimeError("no logic gate found")

def add_imports_to_quantum_code(quantum_code: str) -> str:
    if "QuantumCircuit" in quantum_code:
        return "from qiskit import QuantumCircuit\n" + quantum_code
    return quantum_code

def execute_quantum_circuit(quantum_code: str, shots: int = 1024) -> dict:
    try:
        exec_globals = {
            'QuantumCircuit': QuantumCircuit,
            'Aer': Aer,
            'plot_histogram': plot_histogram,
            'plt': plt,
            'np': np
        }
        exec_locals = {}

        exec(quantum_code, exec_globals, exec_locals)

        qc = exec_locals.get("qc")
        if qc is None:
            raise RuntimeError("Translated code did not create variable `qc`")

        backend = Aer.get_backend("aer_simulator")
        job = backend.run(qc, shots=shots)
        result = job.result()
        counts = result.get_counts()

        # Get all possible states for the number of qubits
        all_states = [format(i, f'0{qc.num_qubits}b') for i in range(2**qc.num_qubits)]
        
        # Initialize all states with 0 counts
        all_counts = {}
        for state in all_states:
            cleaned_state = state.replace(" ", "")
            all_counts[cleaned_state] = 0
        
        # Update with actual counts
        for key, value in counts.items():
            cleaned_key = key.replace(" ", "")
            if len(cleaned_key) > qc.num_qubits:
                cleaned_key = cleaned_key[-qc.num_qubits:]
            all_counts[cleaned_key] = value
        
        # Calculate probabilities for ALL states
        probabilities = {k: v / shots for k, v in all_counts.items()}
        
        circuit_metrics = {
            "depth": qc.depth(),
            "num_qubits": qc.num_qubits,
            "num_gates": qc.size(),
            "gate_counts": dict(qc.count_ops())
        }

        images = {}
        
        try:
            print("Generating circuit diagram...")
            circuit_fig = qc.draw(output='mpl', style={'backgroundcolor': '#EEEEEE'})
            
            buf = io.BytesIO()
            circuit_fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            plt.close(circuit_fig)
            buf.seek(0)
            circuit_base64 = base64.b64encode(buf.read()).decode('utf-8')
            images["circuit_diagram"] = circuit_base64
            
            print("Generating histogram...")
            histogram_fig = create_enhanced_histogram(all_counts, shots)  # Use all_counts here too
            
            buf2 = io.BytesIO()
            histogram_fig.savefig(buf2, format='png', dpi=150, bbox_inches='tight')
            plt.close(histogram_fig)
            buf2.seek(0)
            histogram_base64 = base64.b64encode(buf2.read()).decode('utf-8')
            images["measurement_histogram"] = histogram_base64
            
            print(f"Successfully generated {len(images)} visualizations")
            
        except Exception as viz_error:
            print(f"Warning: Could not generate visualizations: {viz_error}")
            # Create simple text-based fallback
            images["error"] = f"Visualization error: {viz_error}"

        return {
            "success": True,
            "used_generated_code": True,
            "counts": all_counts,  # FIXED: Use all_counts instead of cleaned_counts
            "probabilities": probabilities,
            "circuit_metrics": circuit_metrics,
            "images": images  
        }

    except Exception as e:
        print(f"Execution error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "used_generated_code": False,
            "error": str(e),
            "counts": {},
            "probabilities": {},
            "circuit_metrics": {},
            "images": {}
        }


def create_enhanced_histogram(counts, shots):
    """Create histogram with all basis states displayed"""
    # Get all possible basis states based on qubit count
    max_qubits = max(len(k) for k in counts.keys()) if counts else 2
    all_states = [format(i, f'0{max_qubits}b') for i in range(2**max_qubits)]
    
    # Ensure all states are in counts dictionary
    for state in all_states:
        if state not in counts:
            counts[state] = 0
    
    # Sort by state
    sorted_counts = dict(sorted(counts.items()))
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot bars
    states = list(sorted_counts.keys())
    values = list(sorted_counts.values())
    
    bars = ax.bar(states, values, color='skyblue', edgecolor='black')
    
    # Add value labels
    for bar, value in zip(bars, values):
        if value > 0:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                   f'{value}\n({value/shots:.1%})', ha='center', va='bottom', fontsize=9)
    
    # Set labels and title
    ax.set_xlabel('Measurement Outcome', fontsize=12)
    ax.set_ylabel('Counts', fontsize=12)
    ax.set_title(f'Quantum Measurement Results (Shots: {shots})', fontsize=14, fontweight='bold')
    
    # Set y-axis limit
    if max(values) > 0:
        ax.set_ylim(0, max(values) * 1.15)
    
    # Add grid
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    return fig

# ------------------------------
# Main API endpoint (UPDATED)
# ------------------------------
@app.post("/process-algorithm/")
async def process_algorithm(request: SearchAlgorithmRequest):
    try:
        # Step 1: Extract gate function from the search algorithm
        print(f"Extracting {request.gate_type} gate from Python code...")
        gate_function = extract_gate_function(request.python_code, request.gate_type)
        
        # Step 2: Generate quantum code from the gate function
        print("Generating quantum code...")
        quantum_code_raw = generate_quantum_code(gate_function, max_length=request.max_length)
        
        # Step 3: Add missing imports
        print("Adding imports to quantum code...")
        quantum_code_with_imports = add_imports_to_quantum_code(quantum_code_raw)
        
        # Step 4: Execute the quantum code
        print("Executing quantum circuit...")
        execution_results = execute_quantum_circuit(quantum_code_with_imports, shots=request.shots)
        
        # Step 5: Build response
        response = {
            "processing_summary": {
                "gate_type_extracted": request.gate_type,
                "model_used": "CodeT5",
                "shots_executed": request.shots,
                "execution_success": execution_results.get("success", False)
            },
            "original_python_code": request.python_code,
            "extracted_gate_function": gate_function,
            "generated_quantum_code": {
                "raw_translation": quantum_code_raw,
                "with_imports": quantum_code_with_imports
            },
            "execution_results": {
                "counts": execution_results.get("counts", {}),
                "probabilities": execution_results.get("probabilities", {})
            },
            "circuit_analysis": execution_results.get("circuit_metrics", {}),
            "visualizations_available": False  # Default to False
        }
        
        # Add images if available
        images = execution_results.get("images", {})
        if images and "circuit_diagram" in images:
            response["images"] = images
            response["visualizations_available"] = True
            
        # Add error info if execution failed
        if not execution_results.get("success", False):
            response["execution_error"] = execution_results.get("error", "Unknown error")
            
        return response
        
    except Exception as e:
        print(f"Processing error: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "step": "Processing failed",
                "gate_type": request.gate_type
            }
        )
# ------------------------------
# Test endpoint
# ------------------------------
@app.get("/test/")
async def test_endpoint():
    """Test endpoint to verify server is running"""
    return {
        "status": "active",
        "service": "Python Search Algorithm to Quantum Converter",
        "model_loaded": "CodeT5",
        "supported_gates": ["xor", "or", "and", "not", "nor"]
    }

# ------------------------------
# Example usage endpoint
# ------------------------------
@app.get("/example/")
async def get_example():
    """Get example Python search algorithms with gates"""
    examples = {
        "xor_example": {
            "python_code": """def search_with_xor(arr, target):
    # XOR-based search algorithm
    def xor_gate(a, b):
        return a ^ b
    
    result = None
    for item in arr:
        if xor_gate(item, target) == 0:
            result = item
            break
    return result""",
            "gate_type": "xor",
            "description": "Search algorithm using XOR gate for comparison"
        },
        "or_example": {
            "python_code": """def permission_check(permissions, required):
    # OR-based permission checking
    def or_gate(a, b):
        return a | b
    
    user_access = 0
    for perm in permissions:
        user_access = or_gate(user_access, perm)
    
    return (user_access & required) == required""",
            "gate_type": "or",
            "description": "Permission checking using OR gates"
        }
    }
    return examples

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)