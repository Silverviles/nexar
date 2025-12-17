import os
import requests
import json
import base64
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
import time

# FastAPI server URL (update if needed)
BASE_URL = "http://127.0.0.1:8000"

def get_user_gate():
    """Ask user which gate to test."""
    valid_gates = ["XOR", "OR", "NOT", "NOR"]
    while True:
        print("Which gate do you want to test?")
        print("Options: XOR, OR, NOT, NOR")
        gate = input("Enter your choice: ").strip().upper()
        if gate in valid_gates:
            return gate
        print("Invalid choice. Please select from XOR, OR, NOT, NOR.\n")

def generate_python_code(gate):
    """Generate a simple Python function for the selected gate."""
    if gate == "XOR":
        return "def xor_gate(a, b): return a ^ b"
    elif gate == "OR":
        return "def or_gate(a, b): return a | b"
    elif gate == "NOT":
        return "def not_gate(a): return 1 - a"
    elif gate == "NOR":
        return "def nor_gate(a, b): return 1 - (a | b)"

def execute_python_gate(python_code, gate_name, iterations=1000000):
    """Execute Python gate function many times to measure performance."""
    # Create execution namespace
    exec_globals = {}
    exec_locals = {}
    
    # Execute the Python code to define the function
    exec(python_code, exec_globals, exec_locals)
    
    # Get the gate function
    if gate_name == "XOR":
        func_name = "xor_gate"
    elif gate_name == "OR":
        func_name = "or_gate"
    elif gate_name == "NOT":
        func_name = "not_gate"
    elif gate_name == "NOR":
        func_name = "nor_gate"
    
    gate_func = exec_locals.get(func_name)
    
    if not gate_func:
        raise ValueError(f"Function {func_name} not found in Python code")
    
    # Test all possible inputs
    inputs = []
    if gate_name == "NOT":
        inputs = [(0,), (1,)]
    else:  # 2-input gates
        inputs = [(0, 0), (0, 1), (1, 0), (1, 1)]
    
    # Warm up
    for args in inputs:
        gate_func(*args)
    
    # Time the execution
    start_time = time.perf_counter()
    for _ in range(iterations):
        for args in inputs:
            gate_func(*args)
    end_time = time.perf_counter()
    
    execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
    
    # Calculate results per second
    operations_per_second = (iterations * len(inputs)) / ((end_time - start_time))
    
    return {
        "execution_time_ms": execution_time,
        "operations": iterations * len(inputs),
        "operations_per_second": operations_per_second,
        "time_per_operation_ns": (execution_time * 1_000_000) / (iterations * len(inputs))  # in nanoseconds
    }

def save_to_json(data, folder="results_manual_test", filename=None):
    # Ensure the folder exists
    os.makedirs(folder, exist_ok=True)
    
    # Generate filename if not provided
    if filename is None:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        gate_type = data.get("gate_type", "unknown")
        filename = f"quantum_test_{gate_type}_{timestamp}.json"
    
    # Full path
    filepath = os.path.join(folder, filename)
    
    # Save JSON
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"All results saved to '{filepath}'")
    return filepath

def test_full_flow():
    
    print("=" * 70)
    print("FULL FLOW TEST: Python Code → Quantum Circuit → Execution")
    print("=" * 70)
    
    # Step 0: Ask user which gate
    gate_choice = get_user_gate()
    
    # Step 1: Define Python code
    python_code = generate_python_code(gate_choice)
    
    print(f"\nStep 1: Input Python Code for {gate_choice} Gate")
    print("-" * 40)
    print(python_code)
    
    # Step 2: Call /translate/ endpoint
    print(f"\nStep 2: Translating to Quantum Code...")
    print("-" * 40)
    
    translate_response = requests.post(
        f"{BASE_URL}/translate/",
        json={"python_code": python_code}
    )
    
    if translate_response.status_code != 200:
        print(f"Translation failed: {translate_response.status_code}")
        print(translate_response.text)
        return None
    
    translation = translate_response.json()
    quantum_code_raw = translation["quantum_code"]
    
    print("Translation successful!")
    print(f"Generated Quantum Code:\n{quantum_code_raw}")
    
    # Add imports if needed
    if not quantum_code_raw.startswith("from qiskit"):
        quantum_code_with_imports = f"from qiskit import QuantumCircuit\n{quantum_code_raw}"
    else:
        quantum_code_with_imports = quantum_code_raw
    
    # Step 3: Execute quantum circuit
    print(f"\nStep 3: Executing Quantum Circuit...")
    print("-" * 40)
    
    execute_response = requests.post(
        f"{BASE_URL}/execute/",
        json={
            "quantum_code": quantum_code_with_imports,
            "gate_type": gate_choice.lower(),
            "shots": 1000
        }
    )
    
    if execute_response.status_code != 200:
        print(f"Execution failed: {execute_response.status_code}")
        print(execute_response.text)
        return None
    
    execution = execute_response.json()
    
    print("Execution successful!")
    
    print(f"\nStep 4: Execution Results")
    print("-" * 40)
    
    print(f"Success: {execution['success']}")
    print(f"Used Generated Code: {execution.get('used_generated_code', True)}")
    
    if 'fallback_reason' in execution:
        print(f"Fallback Reason: {execution['fallback_reason']}")
    
    print(f"\nMeasurement Counts:")
    for state, count in execution['counts'].items():
        prob = execution['probabilities'][state]
        print(f"  {state}: {count} times ({prob:.2%})")
    
    print(f"\nCircuit Analysis:")
    perf = execution['performance']
    print(f"  Depth: {perf['depth']}")
    print(f"  Number of Qubits: {perf['num_qubits']}")
    print(f"  Total Gates: {perf['num_gates']}")
    print(f"  Execution Time: {perf['execution_time_seconds']:.4f} seconds")
    
    print(f"\nGate Counts Breakdown:")
    gate_counts = perf['gate_counts']
    if gate_counts:
        for gate_type, count in gate_counts.items():
            print(f"  {gate_type}: {count}")
    else:
        print("  No gate count information available")
    
    # Step 5: Compare with Python execution
    print(f"\nStep 5: Performance Comparison")
    print("-" * 40)
    
    python_perf_data = None
    try:
        print("Testing Python gate execution speed...")
        python_perf = execute_python_gate(python_code, gate_choice, iterations=1000000)
        python_perf_data = python_perf
        
        quantum_time_ms = perf.get('execution_time_seconds', 0) * 1000
        
        print(f"\nQuantum Simulation:")
        print(f"  Execution Time: {quantum_time_ms:.2f} ms")
        print(f"  Operations (shots): {1000}")
        print(f"  Time per operation: {quantum_time_ms / 1000:.6f} ms")
        
        print(f"\nPython Execution:")
        print(f"  Execution Time: {python_perf['execution_time_ms']:.2f} ms")
        print(f"  Operations: {python_perf['operations']:,}")
        print(f"  Time per operation: {python_perf['time_per_operation_ns']:.2f} ns")
        print(f"  Operations per second: {python_perf['operations_per_second']:,.0f}")
        
        if quantum_time_ms > 0 and python_perf['time_per_operation_ns'] > 0:
            quantum_per_op_ms = quantum_time_ms / 1000
            python_per_op_ms = python_perf['time_per_operation_ns'] / 1_000_000
            
            speed_difference = quantum_per_op_ms / python_per_op_ms
            
            print(f"\nPerformance Comparison:")
            print(f"  Python is {speed_difference:,.0f}x faster per operation")
            print(f"  Quantum simulation takes {quantum_per_op_ms / python_per_op_ms:,.0f}x longer per operation")

            if speed_difference > 1:
                print(f"  ➜ Python is FASTER (by {speed_difference:,.0f}x)")
                print(f"  ➜ Quantum simulation is SLOWER")
            else:
                print(f"  ➜ Quantum simulation is FASTER")
                print(f"  ➜ Python is SLOWER")
                
    except Exception as e:
        print(f"Could not run Python comparison: {e}")
    
    # Step 6: Display visualizations (popup)
    if 'images' in execution:
        print(f"\nStep 6: Circuit Visualizations (Popup)")
        print("-" * 40)
        
        images = execution['images']
        
        # Display circuit diagram
        if 'circuit_diagram' in images:
            print("Displaying Circuit Diagram...")
            img_data = base64.b64decode(images['circuit_diagram'])
            img = Image.open(BytesIO(img_data))
            
            # Display histogram
            if 'measurement_histogram' in images:
                print("Displaying Measurement Histogram...")
                hist_data = base64.b64decode(images['measurement_histogram'])
                hist_img = Image.open(BytesIO(hist_data))
                
                # Show both images in matplotlib
                plt.figure(figsize=(12, 5))
                
                plt.subplot(1, 2, 1)
                plt.title("Circuit Diagram")
                plt.imshow(img)
                plt.axis('off')
                
                plt.subplot(1, 2, 2)
                plt.title("Measurement Histogram")
                plt.imshow(hist_img)
                plt.axis('off')
                
                plt.tight_layout()
                plt.show()
            else:
                # Show only circuit diagram
                plt.figure(figsize=(6, 5))
                plt.title("Circuit Diagram")
                plt.imshow(img)
                plt.axis('off')
                plt.show()
    
    # Step 7: Prepare complete results for JSON
    print(f"\nStep 7: Preparing Complete Results")
    print("-" * 40)
    
    # Build complete results dictionary
    complete_results = {
        "test_metadata": {
            "gate_type": gate_choice,
            "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "shots_executed": 1000,
            "server_url": BASE_URL
        },
        "original_python_code": python_code,
        "translation_results": {
            "raw_quantum_code": quantum_code_raw,
            "quantum_code_with_imports": quantum_code_with_imports,
            "translation_success": True
        },
        "quantum_execution": {
            "success": execution['success'],
            "used_generated_code": execution.get('used_generated_code', True),
            "fallback_reason": execution.get('fallback_reason', None),
            "counts": execution['counts'],
            "probabilities": execution['probabilities'],
            "circuit_analysis": {
                "depth": perf['depth'],
                "num_qubits": perf['num_qubits'],
                "num_gates": perf['num_gates'],
                "gate_counts": perf['gate_counts'],
                "execution_time_seconds": perf['execution_time_seconds']
            }
        },
        "performance_comparison": {
            "quantum_simulation": {
                "execution_time_seconds": perf['execution_time_seconds'],
                "execution_time_ms": perf['execution_time_seconds'] * 1000,
                "shots": 1000,
                "shots_per_second": 1000 / perf['execution_time_seconds'] if perf['execution_time_seconds'] > 0 else 0
            }
        }
    }
    
    # Add Python performance if available
    if python_perf_data:
        complete_results["performance_comparison"]["python_execution"] = {
            "execution_time_ms": python_perf_data['execution_time_ms'],
            "execution_time_seconds": python_perf_data['execution_time_ms'] / 1000,
            "operations": python_perf_data['operations'],
            "operations_per_second": python_perf_data['operations_per_second'],
            "time_per_operation_ns": python_perf_data['time_per_operation_ns']
        }
        
        # Calculate comparison metrics
        quantum_time = perf['execution_time_seconds'] * 1000
        python_time = python_perf_data['execution_time_ms']
        
        if python_time > 0:
            speed_factor = quantum_time / python_time if python_time > 0 else 0

            complete_results["performance_comparison"]["speed_comparison"] = {
                "python_vs_quantum_speed_ratio": python_perf_data['operations_per_second'] / (1000 / perf['execution_time_seconds']) if perf['execution_time_seconds'] > 0 else 0,
                "quantum_time_per_shot_ms": quantum_time / 1000,
                "python_time_per_operation_ns": python_perf_data['time_per_operation_ns'],
                "python_is_faster_by_factor": speed_factor,
                "faster_implementation": "Python" if speed_factor > 1 else "Quantum" if speed_factor < 1 else "Equal"
            }
            
            if speed_factor > 1:
                faster_statement = f"Python is {speed_factor:,.1f}x faster than Quantum simulation"
            elif speed_factor < 1:
                faster_statement = f"Quantum simulation is {1/speed_factor:,.1f}x faster than Python"
            else:
                faster_statement = "Python and Quantum simulation have equal speed"
            
            complete_results["performance_comparison"]["comparison_summary"] = faster_statement
    
    complete_results["visualizations"] = {
        "circuit_diagram_available": 'circuit_diagram' in execution.get('images', {}),
        "histogram_available": 'measurement_histogram' in execution.get('images', {}),
        "note": "Images displayed as popup, not saved in JSON"
    }
    
    # Add summary section
    complete_results["summary"] = {
        "gate_type_tested": gate_choice,
        "circuit_complexity": "Simple" if perf['depth'] < 5 else "Moderate" if perf['depth'] < 10 else "Complex",
        "total_unique_states": len(execution['counts']),
        "most_probable_state": max(execution['probabilities'].items(), key=lambda x: x[1])[0] if execution['probabilities'] else "None",
        "translation_quality": "Good" if execution.get('used_generated_code', False) else "Fallback Used"
    }
    
    print(f"Complete results prepared for {gate_choice} gate test")
    print(f"  • Original Python code")
    print(f"  • Generated quantum code (with imports)")
    print(f"  • Execution results and counts")
    print(f"  • Circuit analysis metrics")
    print(f"  • Performance comparison data")
    print(f"  • Summary information")
    
    print(f"\n{'='*70}")
    print("FULL FLOW TEST COMPLETE!")
    print(f"{'='*70}")
    
    return complete_results

def display_results_summary(results):
    """Display a summary of the saved results."""
    print(f"\nResults Summary:")
    print("-" * 40)
    
    gate_type = results.get("test_metadata", {}).get("gate_type", "Unknown")
    timestamp = results.get("test_metadata", {}).get("test_timestamp", "Unknown")
    
    print(f"Gate Type: {gate_type}")
    print(f"Test Time: {timestamp}")
    
    # Quantum execution summary
    quantum_exec = results.get("quantum_execution", {})
    if quantum_exec.get("success", False):
        counts = quantum_exec.get("counts", {})
        total_shots = sum(counts.values())
        print(f"Quantum Execution: SUCCESS")
        print(f"Total Shots: {total_shots}")
        print(f"Unique States: {len(counts)}")
        
        # Show top 3 most probable states
        probs = quantum_exec.get("probabilities", {})
        if probs:
            sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:3]
            print("Top 3 States:")
            for state, prob in sorted_probs:
                print(f"  {state}: {prob:.2%}")
    
    # Circuit analysis
    circuit_analysis = quantum_exec.get("circuit_analysis", {})
    print(f"Circuit Depth: {circuit_analysis.get('depth', 'N/A')}")
    print(f"Number of Qubits: {circuit_analysis.get('num_qubits', 'N/A')}")
    print(f"Total Gates: {circuit_analysis.get('num_gates', 'N/A')}")

if __name__ == "__main__":
    print("Make sure your FastAPI server is running on http://127.0.0.1:8000")
    print("Starting full flow test...\n")
    
    try:
        # Run the test
        results = test_full_flow()
        
        if results:
            # Save to JSON file
            print(f"\nSaving all results to JSON file...")
            filename = save_to_json(results)
            
            # Display summary
            display_results_summary(results)
            
                
    except requests.exceptions.ConnectionError:
        print("Cannot connect to FastAPI server!")
        print("Please start your server first with: uvicorn your_api_file:app --reload")
    except Exception as e:
        print(f"Error during test: {e}")