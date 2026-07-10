import requests
import json
import base64
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image

# FastAPI server URL (update if needed)
BASE_URL = "http://127.0.0.1:8001"

def test_full_flow():
    """Test the complete flow: Python → Translation → Execution"""
    
    print("=" * 70)
    print("FULL FLOW TEST: Python Code → Quantum Circuit → Execution")
    print("=" * 70)
    
    # Step 1: Define Python code (XOR example)
    python_code = "def xor(a, b): return a ^ b"
    
    print(f"\n📝 Step 1: Input Python Code")
    print("-" * 40)
    print(python_code)
    
    # Step 2: Call /translate/ endpoint
    print(f"\n🔄 Step 2: Translating to Quantum Code...")
    print("-" * 40)
    
    translate_response = requests.post(
        f"{BASE_URL}/translate/",
        json={"python_code": python_code}
    )
    
    if translate_response.status_code != 200:
        print(f"❌ Translation failed: {translate_response.status_code}")
        print(translate_response.text)
        return
    
    translation = translate_response.json()
    quantum_code = translation["quantum_code"]
    
    print("✅ Translation successful!")
    print(f"Generated Quantum Code:\n{quantum_code}")
    
    # Step 3: Add import (if needed by your API)
    # Your model outputs clean code, but execution might need import
    if not quantum_code.startswith("from qiskit"):
        quantum_code_with_import = f"from qiskit import QuantumCircuit\n{quantum_code}"
    else:
        quantum_code_with_import = quantum_code
    
    # Step 4: Call /execute/ endpoint
    print(f"\n⚡ Step 3: Executing Quantum Circuit...")
    print("-" * 40)
    
    execute_response = requests.post(
        f"{BASE_URL}/execute/",
        json={
            "quantum_code": quantum_code_with_import,
            "gate_type": "xor",
            "shots": 1000
        }
    )
    
    if execute_response.status_code != 200:
        print(f"❌ Execution failed: {execute_response.status_code}")
        print(execute_response.text)
        return
    
    execution = execute_response.json()
    
    print("✅ Execution successful!")
    
    # Step 5: Display results
    print(f"\n📊 Step 4: Results")
    print("-" * 40)
    
    print(f"Success: {execution['success']}")
    print(f"Used Generated Code: {execution.get('used_generated_code', True)}")
    
    if 'fallback_reason' in execution:
        print(f"Fallback Reason: {execution['fallback_reason']}")
    
    print(f"\n📈 Measurement Counts:")
    for state, count in execution['counts'].items():
        prob = execution['probabilities'][state]
        print(f"  {state}: {count} times ({prob:.2%})")
    
    print(f"\n⚙️ Performance Metrics:")
    perf = execution['performance']
    print(f"  Depth: {perf['depth']}")
    print(f"  Qubits: {perf['num_qubits']}")
    print(f"  Gates: {perf['num_gates']}")
    print(f"  Gate Counts: {perf['gate_counts']}")
    print(f"  Execution Time: {perf['execution_time_seconds']:.4f}s")
    
    # Step 6: Display images if available
    if 'images' in execution:
        print(f"\n🖼️ Step 5: Circuit Visualizations")
        print("-" * 40)
        
        images = execution['images']
        
        # Display circuit diagram
        if 'circuit_diagram' in images:
            print("📋 Circuit Diagram (saved as 'circuit.png')")
            img_data = base64.b64decode(images['circuit_diagram'])
            img = Image.open(BytesIO(img_data))
            img.save('circuit.png')
            print("  ✅ Saved as circuit.png")
        
        # Display histogram
        if 'measurement_histogram' in images:
            print("📊 Measurement Histogram (saved as 'histogram.png')")
            img_data = base64.b64decode(images['measurement_histogram'])
            img = Image.open(BytesIO(img_data))
            img.save('histogram.png')
            print("  ✅ Saved as histogram.png")
            
            # Also show histogram in matplotlib
            plt.figure(figsize=(10, 5))
            
            plt.subplot(1, 2, 1)
            plt.title("Circuit Diagram")
            circuit_img = Image.open('circuit.png')
            plt.imshow(circuit_img)
            plt.axis('off')
            
            plt.subplot(1, 2, 2)
            plt.title("Measurement Histogram")
            hist_img = Image.open('histogram.png')
            plt.imshow(hist_img)
            plt.axis('off')
            
            plt.tight_layout()
            plt.show()
    
    print(f"\n{'='*70}")
    print("✅ FULL FLOW TEST COMPLETE!")
    print(f"{'='*70}")

if __name__ == "__main__":
    # Make sure your FastAPI server is running first!
    print("Make sure your FastAPI server is running on http://127.0.0.1:8001")
    print("Starting full flow test...\n")
    
    try:
        test_full_flow()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to FastAPI server!")
        print("Please start your server first with: uvicorn your_api_file:app --reload")
    except Exception as e:
        print(f"❌ Error during test: {e}")
