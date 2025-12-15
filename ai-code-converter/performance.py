import requests
import json
import time
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class QuantumPerformanceAnalyzer:
    def __init__(self, api_url="http://127.0.0.1:8000"):
        self.api_url = api_url
        self.simulator = Aer.get_backend('aer_simulator')
    
    def full_pipeline(self, python_code, gate_type="xor", shots=1000):
        """Complete pipeline: Translate → Execute → Analyze Performance"""
        
        print("=" * 80)
        print("QUANTUM PERFORMANCE PIPELINE")
        print(f"Input: {python_code[:60]}...")
        print("=" * 80)
        
        results = {
            "python_code": python_code,
            "gate_type": gate_type,
            "shots": shots
        }
        
        # STEP 1: TRANSLATE
        print("\n🔗 Step 1: Translating Python to Quantum...")
        try:
            translate_response = requests.post(
                f"{self.api_url}/translate/",
                json={"python_code": python_code},
                timeout=10
            )
            
            if translate_response.status_code != 200:
                print(f"❌ Translation failed: {translate_response.status_code}")
                return None
            
            translation = translate_response.json()
            quantum_code = translation["quantum_code"]
            results["quantum_code"] = quantum_code
            print(f"✅ Translation successful!")
            print(f"   Generated quantum code")
        except Exception as e:
            print(f"❌ Translation error: {e}")
            return None
        
        # STEP 2: EXECUTE
        print("\n⚡ Step 2: Executing Quantum Circuit...")
        try:
            # Add import for execution
            if not quantum_code.startswith("from qiskit"):
                exec_code = f"from qiskit import QuantumCircuit\n{quantum_code}"
            else:
                exec_code = quantum_code
            
            execute_response = requests.post(
                f"{self.api_url}/execute/",
                json={
                    "quantum_code": exec_code,
                    "gate_type": gate_type,
                    "shots": shots
                },
                timeout=30
            )
            
            if execute_response.status_code != 200:
                print(f"❌ Execution failed: {execute_response.status_code}")
                return None
            
            execution = execute_response.json()
            results["execution"] = execution
            print(f"✅ Execution successful!")
            print(f"   Circuit executed with {shots} shots")
            
            # Show measurement distribution
            counts = execution["counts"]
            total = sum(counts.values())
            print(f"   Measurement distribution:")
            for state, count in counts.items():
                percentage = (count / total) * 100
                print(f"     {state}: {count} ({percentage:.1f}%)")
        
        except Exception as e:
            print(f"❌ Execution error: {e}")
            return None
        
        # STEP 3: PERFORMANCE PREDICTION
        print("\n📊 Step 3: Performance Prediction...")
        performance = self._analyze_performance(python_code, quantum_code, shots)
        results["performance_prediction"] = performance
        
        # STEP 4: DISPLAY RESULTS
        self._display_results(results)
        
        # Save results
        timestamp = int(time.time())
        filename = f"quantum_analysis_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
        print("=" * 80)
        
        return results
    
    def _analyze_performance(self, python_code, quantum_code, shots=1000):
        """Analyze classical vs quantum performance"""
        performance = {}
        
        # Measure classical execution time
        print("   Measuring classical performance...")
        classical_time = self._measure_classical_time(python_code)
        performance["classical_time_ms"] = classical_time
        
        # Measure quantum execution time (from execution results if available)
        print("   Measuring quantum performance...")
        
        # First try to get actual execution time from API results
        quantum_time = None
        
        # If we have execution results, use the actual time
        if "execution" in locals() and "performance" in locals()["execution"]:
            exec_time = locals()["execution"]["performance"].get("execution_time_seconds", 0)
            if exec_time > 0:
                quantum_time = exec_time * 1000  # Convert to ms
                performance["quantum_time_ms"] = quantum_time
                performance["time_source"] = "actual_execution"
        
        # If not, estimate from circuit
        if quantum_time is None:
            quantum_time = self._estimate_quantum_time(quantum_code, shots)
            performance["quantum_time_ms"] = quantum_time
            performance["time_source"] = "estimated"
        
        # Calculate speedup
        if classical_time and quantum_time:
            speedup = classical_time / quantum_time if quantum_time > 0 else 0
            performance["speedup"] = speedup
            performance["has_quantum_advantage"] = speedup > 1.0
            
            # Calculate quantum advantage metrics
            performance["classical_per_operation"] = classical_time / 1000  # per 1000 operations
            performance["quantum_per_shot"] = quantum_time / shots
        
        # Analyze circuit complexity
        circuit_metrics = self._analyze_circuit_complexity(quantum_code)
        performance.update(circuit_metrics)
        
        return performance
    
    def _measure_classical_time(self, python_code, iterations=10000):
        """Measure classical Python execution time"""
        try:
            # Extract function if it's a function definition
            if "def " in python_code:
                # Find function name
                func_line = python_code.split("\n")[0]
                func_name = func_line.split("def ")[1].split("(")[0]
                
                # Create test code
                test_code = f"""
import time
{python_code}

def benchmark():
    start = time.perf_counter()
    for a in [0, 1]:
        for b in [0, 1]:
            for _ in range({iterations // 4}):
                result = {func_name}(a, b)
    end = time.perf_counter()
    return (end - start) * 1000  # ms
"""
            else:
                # For expressions
                test_code = f"""
import time

def benchmark():
    start = time.perf_counter()
    for a in [0, 1]:
        for b in [0, 1]:
            for _ in range({iterations // 4}):
                result = {python_code}
    end = time.perf_counter()
    return (end - start) * 1000  # ms
"""
            
            exec_globals = {}
            exec(test_code, exec_globals)
            exec_time = eval("benchmark()", exec_globals)
            
            return exec_time
            
        except Exception as e:
            print(f"   ⚠️ Could not measure classical time: {e}")
            # Return estimated time based on operation complexity
            return 10.0  # ms (default estimate)
    
    def _estimate_quantum_time(self, quantum_code, shots):
        """Estimate quantum execution time from circuit"""
        try:
            # Parse the circuit
            exec_globals = {'QuantumCircuit': QuantumCircuit, 'qc': None}
            exec_locals = {}
            
            if not quantum_code.startswith("from qiskit"):
                exec_code = f"from qiskit import QuantumCircuit\n{quantum_code}"
            else:
                exec_code = quantum_code
            
            exec(exec_code, exec_globals, exec_locals)
            qc = exec_locals.get('qc')
            
            if qc is None:
                return 5.0  # Default estimate
            
            # Estimate based on circuit complexity
            depth = qc.depth()
            num_qubits = qc.num_qubits
            num_gates = qc.size()
            
            # Estimation formula (adjust based on your observations)
            base_time = 0.5  # ms base overhead
            gate_time = 0.002  # ms per gate
            qubit_time = 0.01  # ms per qubit
            shot_time = 0.0001  # ms per shot
            
            estimated = base_time + \
                       (num_gates * gate_time) + \
                       (num_qubits * qubit_time) + \
                       (shots * shot_time)
            
            return max(estimated, 1.0)  # At least 1 ms
            
        except Exception as e:
            print(f"   ⚠️ Could not estimate quantum time: {e}")
            return 5.0  # Default estimate
    
    def _analyze_circuit_complexity(self, quantum_code):
        """Analyze quantum circuit complexity"""
        metrics = {}
        
        try:
            exec_globals = {'QuantumCircuit': QuantumCircuit, 'qc': None}
            exec_locals = {}
            
            if not quantum_code.startswith("from qiskit"):
                exec_code = f"from qiskit import QuantumCircuit\n{quantum_code}"
            else:
                exec_code = quantum_code
            
            exec(exec_code, exec_globals, exec_locals)
            qc = exec_locals.get('qc')
            
            if qc:
                metrics["circuit_qubits"] = qc.num_qubits
                metrics["circuit_depth"] = qc.depth()
                metrics["circuit_gates"] = qc.size()
                metrics["gate_counts"] = dict(qc.count_ops())
                
                # Check quantum features
                metrics["has_superposition"] = any(g.operation.name == 'h' for g in qc.data)
                metrics["has_entanglement"] = any(g.operation.name in ['cx', 'cz', 'swap'] for g in qc.data)
                metrics["has_measurement"] = any(g.operation.name == 'measure' for g in qc.data)
        
        except Exception as e:
            print(f"   ⚠️ Could not analyze circuit: {e}")
        
        return metrics
    
    def _display_results(self, results):
        """Display formatted results"""
        print("\n" + "=" * 80)
        print("PERFORMANCE ANALYSIS RESULTS")
        print("=" * 80)
        
        perf = results.get("performance_prediction", {})
        exec_data = results.get("execution", {})
        
        # Classical vs Quantum timing
        print("\n⏱️ TIMING ANALYSIS")
        print("-" * 40)
        
        classical_time = perf.get("classical_time_ms")
        quantum_time = perf.get("quantum_time_ms")
        time_source = perf.get("time_source", "estimated")
        
        if classical_time and quantum_time:
            print(f"Classical Execution: {classical_time:.2f} ms")
            print(f"Quantum Execution ({time_source}): {quantum_time:.2f} ms")
            
            speedup = perf.get("speedup", 0)
            if speedup > 0:
                print(f"\n⚡ SPEEDUP: {speedup:.2f}x")
                
                if speedup > 1.0:
                    print(f"✅ QUANTUM ADVANTAGE: {speedup:.1f}x faster")
                else:
                    print(f"⚠️ Classical is {1/speedup:.1f}x faster")
        
        # Circuit Analysis
        print("\n🔧 CIRCUIT ANALYSIS")
        print("-" * 40)
        
        if "circuit_qubits" in perf:
            print(f"Qubits: {perf['circuit_qubits']}")
            print(f"Depth: {perf['circuit_depth']}")
            print(f"Total Gates: {perf['circuit_gates']}")
            
            if "gate_counts" in perf:
                print("Gate Counts:")
                for gate, count in perf["gate_counts"].items():
                    print(f"  {gate}: {count}")
        
        # Quantum Features
        print("\n🎯 QUANTUM FEATURES")
        print("-" * 40)
        
        features = [
            ("Superposition", perf.get("has_superposition", False)),
            ("Entanglement", perf.get("has_entanglement", False)),
            ("Measurement", perf.get("has_measurement", False))
        ]
        
        for feature, present in features:
            status = "✅ Present" if present else "❌ Absent"
            print(f"{feature}: {status}")
        
        # Execution Results
        if exec_data and "counts" in exec_data:
            print("\n📈 MEASUREMENT RESULTS")
            print("-" * 40)
            
            counts = exec_data["counts"]
            total = sum(counts.values())
            
            for state in sorted(counts.keys()):
                count = counts[state]
                percentage = (count / total) * 100
                print(f"{state}: {'█' * int(percentage/5)} {count} ({percentage:.1f}%)")

# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = QuantumPerformanceAnalyzer()
    
    # Test cases - these will go through the full pipeline
    test_cases = [
        # XOR examples
        ("def xor(a, b): return a ^ b", "xor"),
        ("result = a ^ b", "xor"),
        
        # OR examples
        ("def or_gate(a, b): return a | b", "or"),
        ("return a or b", "or"),
        
        # AND examples
        ("def and_gate(a, b): return a & b", "and"),
        ("result = a and b", "and"),
        
        # NOT examples
        ("def not_gate(bit): return 1 - bit", "not"),
        ("return not bit", "not"),
    ]
    
    print("QUANTUM PERFORMANCE ANALYSIS TEST SUITE")
    print("Testing with various Python logic gates...\n")
    
    # Run first test case
    python_code, gate_type = test_cases[0]
    results = analyzer.full_pipeline(python_code, gate_type)
    
    # Optionally run more tests
    """
    for python_code, gate_type in test_cases[1:3]:  # Test first 3
        print("\n" + "="*80)
        print(f"Testing: {python_code[:50]}...")
        print("="*80)
        results = analyzer.full_pipeline(python_code, gate_type)
        time.sleep(2)  # Small delay between tests
    """