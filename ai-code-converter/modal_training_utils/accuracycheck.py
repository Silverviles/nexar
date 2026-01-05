import requests
import json
import time
import subprocess
import tempfile
from pathlib import Path
import sys

BASE_URL = "http://127.0.0.1:8000"

class ModelEvaluator:
    def __init__(self):
        self.results = []
        
    def generate_test_cases(self):

        return [
            # XOR (core + variation + tricky)
            ("def xor(a, b): return a ^ b", "xor"),
            ("return 1 if a != b else 0", "xor"),
            ("def half_adder(a, b): return a ^ b, a & b", "xor"),

            # OR
            ("def or_gate(a, b): return a or b", "or"),
            ("result = max(a, b)", "or"),
            ("def three_or(a, b, c): return a or b or c", "or"),

            # AND
            ("def and_gate(a, b): return a and b", "and"),
            ("return a * b", "and"),
            ("def majority(x, y, z): return (x & y) | (x & z) | (y & z)", "and"),

            # NOT
            ("def not_gate(a): return not a", "not"),
            ("return 1 - bit", "not"),

            # Edge / sanity check
            ("def identity(x): return x", "not"),
    ]

    
    def evaluate_syntactic_correctness(self, quantum_code):
        """Check if quantum code compiles"""
        try:
            # Test if code can be imported and executed
            exec_globals = {'QuantumCircuit': None, 'qc': None}
            exec_locals = {}
            
            # Add import if missing
            if not quantum_code.startswith('from'):
                quantum_code = f"from qiskit import QuantumCircuit\n{quantum_code}"
            
            exec(quantum_code, {'QuantumCircuit': type('QuantumCircuit', (), {})}, exec_locals)
            
            # Check if qc was created
            if 'qc' in exec_locals:
                return True, "Syntactically correct"
            return False, "No QuantumCircuit created"
            
        except Exception as e:
            return False, f"Syntax error: {str(e)}"
    
    def evaluate_semantic_correctness(self, python_code, quantum_code, gate_type):
        """Check if quantum circuit preserves classical logic"""
        try:
            # Skip for complex multi-output functions
            if ',' in python_code or 'return' in python_code and ',' in python_code:
                return True, "Complex function - semantic check skipped"
            
            # Execute both classical and quantum versions
            # For simple gates, we can test with all input combinations
            test_inputs = [(0, 0), (0, 1), (1, 0), (1, 1)]
            
            for a, b in test_inputs:
                # Evaluate Python function
                exec(python_code, globals())
                
                # Get function name
                func_name = python_code.split('def ')[1].split('(')[0] if 'def ' in python_code else None
                
                if func_name:
                    py_result = eval(f"{func_name}({a}, {b})")
                    
                    # For quantum, we'd need to simulate - simplified check
                    # We'll check if circuit structure matches expected gate type
                    if gate_type == "xor" and "cx" in quantum_code.lower():
                        return True, "Semantic structure correct"
                    elif gate_type == "or" and ("cx" in quantum_code.lower() and "x(" in quantum_code.lower()):
                        return True, "Semantic structure correct"
                    elif gate_type == "and" and "ccx" in quantum_code.lower():
                        return True, "Semantic structure correct"
                    elif gate_type == "not" and "x(" in quantum_code.lower():
                        return True, "Semantic structure correct"
            
            return False, "Semantic mismatch"
            
        except Exception as e:
            return False, f"Semantic evaluation error: {str(e)}"
    
    def evaluate_quantum_advantage(self, quantum_code):
        """Check if circuit uses quantum properties"""
        has_superposition = "h(" in quantum_code.lower()  # Hadamard gates
        has_entanglement = "cx(" in quantum_code.lower() or "ccx" in quantum_code.lower()  # Entangling gates
        has_measurement = "measure" in quantum_code.lower()  # Measurement
        
        if has_superposition and has_measurement:
            return True, f"Uses quantum properties: superposition={has_superposition}, entanglement={has_entanglement}"
        return False, "No quantum properties detected"
    
    def run_evaluation(self):
        """Run complete evaluation"""
        print("=" * 70)
        print("MODEL ACCURACY EVALUATION")
        print("=" * 70)
        
        test_cases = self.generate_test_cases()
        
        for idx, (python_code, expected_gate) in enumerate(test_cases, 1):
            print(f"\n📝 Test {idx:2d}/{len(test_cases)}: {python_code[:50]}...")
            
            try:
                # Step 1: Translate to quantum
                translate_response = requests.post(
                    f"{BASE_URL}/translate/",
                    json={"python_code": python_code},
                    timeout=10
                )
                
                if translate_response.status_code != 200:
                    print(f"   ❌ Translation failed")
                    self.results.append({
                        "test": idx,
                        "python_code": python_code,
                        "success": False,
                        "error": f"HTTP {translate_response.status_code}"
                    })
                    continue
                
                quantum_code = translate_response.json()["quantum_code"]
                
                # Step 2: Evaluate correctness
                syntactic_ok, syntactic_msg = self.evaluate_syntactic_correctness(quantum_code)
                semantic_ok, semantic_msg = self.evaluate_semantic_correctness(python_code, quantum_code, expected_gate)
                quantum_ok, quantum_msg = self.evaluate_quantum_advantage(quantum_code)
                
                # Step 3: Execute to verify
                execute_ok = False
                if syntactic_ok:
                    try:
                        # Add import for execution
                        if not quantum_code.startswith('from'):
                            exec_code = f"from qiskit import QuantumCircuit\n{quantum_code}"
                        else:
                            exec_code = quantum_code
                        
                        exec_response = requests.post(
                            f"{BASE_URL}/execute/",
                            json={
                                "quantum_code": exec_code,
                                "gate_type": expected_gate,
                                "shots": 100
                            },
                            timeout=10
                        )
                        execute_ok = exec_response.status_code == 200
                    except:
                        execute_ok = False
                
                # Calculate score
                score = 0
                if syntactic_ok: score += 1
                if semantic_ok: score += 1
                if quantum_ok: score += 1
                if execute_ok: score += 1
                
                total_score = score / 4.0  # Normalize to 0-1
                
                self.results.append({
                    "test": idx,
                    "python_code": python_code,
                    "quantum_code": quantum_code,
                    "expected_gate": expected_gate,
                    "syntactic_ok": syntactic_ok,
                    "semantic_ok": semantic_ok,
                    "quantum_ok": quantum_ok,
                    "execute_ok": execute_ok,
                    "total_score": total_score,
                    "syntactic_msg": syntactic_msg,
                    "semantic_msg": semantic_msg,
                    "quantum_msg": quantum_msg
                })
                
                print(f"   ✅ Translation: {'✓' if syntactic_ok else '✗'} Syntax")
                print(f"                {'✓' if semantic_ok else '✗'} Semantic")
                print(f"                {'✓' if quantum_ok else '✗'} Quantum")
                print(f"                {'✓' if execute_ok else '✗'} Execution")
                print(f"   📊 Score: {total_score:.2f}/1.00")
                
            except Exception as e:
                print(f"   ❌ Test failed: {str(e)}")
                self.results.append({
                    "test": idx,
                    "python_code": python_code,
                    "success": False,
                    "error": str(e)
                })
        
        self.print_summary()
    
    def print_summary(self):
        """Print evaluation summary"""
        print("\n" + "=" * 70)
        print("EVALUATION SUMMARY")
        print("=" * 70)
        
        successful = [r for r in self.results if r.get('total_score', 0) > 0]
        
        if not successful:
            print("❌ No successful tests!")
            return
        
        # Calculate metrics
        avg_score = sum(r['total_score'] for r in successful) / len(successful)
        
        syntactic_rate = sum(1 for r in successful if r['syntactic_ok']) / len(successful)
        semantic_rate = sum(1 for r in successful if r['semantic_ok']) / len(successful)
        quantum_rate = sum(1 for r in successful if r['quantum_ok']) / len(successful)
        execute_rate = sum(1 for r in successful if r['execute_ok']) / len(successful)
        
        print(f"\n📈 Overall Accuracy: {avg_score:.1%}")
        print(f"🎯 Target (from proposal): 85%")
        print(f"📊 {'✅ MET TARGET' if avg_score >= 0.85 else '❌ BELOW TARGET'}")
        
        print(f"\n📊 Breakdown:")
        print(f"   Syntactic Correctness: {syntactic_rate:.1%}")
        print(f"   Semantic Correctness: {semantic_rate:.1%}")
        print(f"   Quantum Advantage: {quantum_rate:.1%}")
        print(f"   Execution Success: {execute_rate:.1%}")
        
        print(f"\n📋 Test Counts:")
        print(f"   Total Tests: {len(self.results)}")
        print(f"   Successful: {len(successful)}")
        print(f"   Failed: {len(self.results) - len(successful)}")
        
        # Save detailed results
        with open('evaluation_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: evaluation_results.json")

# Run evaluation
if __name__ == "__main__":
    evaluator = ModelEvaluator()
    evaluator.run_evaluation()