"""
Regression Test Suite
Ensures existing (non-recursive) functionality is not broken
by new recursion analysis features

Tests: Language detection, AST building, basic complexity analysis
"""
import sys
import os
import json
from typing import Dict, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.language_detector import LanguageDetector, SupportedLanguage
from modules.ast_builder import ASTBuilder
from modules.complexity_analyzer import ComplexityAnalyzer
from models.analysis_result import TimeComplexity


class RegressionTestSuite:
    """Regression tests for existing functionality"""
    
    def __init__(self):
        self.detector = LanguageDetector()
        self.ast_builder = ASTBuilder()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def test_python_language_detection(self):
        """Test Python language detection"""
        code = """
def hello(name):
    print(f"Hello {name}")
    
hello("World")
        """
        
        result = self.detector.detect(code)
        success = result['language'] == 'python' and result['confidence'] > 0.5
        
        self._record_result(
            "Python Language Detection",
            success,
            f"Language: {result['language']}, Confidence: {result['confidence']:.2f}"
        )
        return success
    
    def test_qiskit_language_detection(self):
        """Test Qiskit language detection"""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
        """
        
        result = self.detector.detect(code)
        success = result['language'] == 'qiskit' and result['confidence'] > 0.5
        
        self._record_result(
            "Qiskit Language Detection",
            success,
            f"Language: {result['language']}, Confidence: {result['confidence']:.2f}"
        )
        return success
    
    def test_simple_loop_analysis(self):
        """Test simple loop analysis"""
        code = """
def sum_array(arr):
    total = 0
    for num in arr:
        total += num
    return total
        """
        
        try:
            unified_ast = self.ast_builder.build(code, SupportedLanguage.PYTHON)
            
            # Should detect it's Python with loops
            success = unified_ast is not None
            
            self._record_result(
                "Simple Loop Analysis",
                success,
                "AST built successfully"
            )
            return success
        except Exception as e:
            self._record_result(
                "Simple Loop Analysis",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_nested_loop_analysis(self):
        """Test nested loop analysis"""
        code = """
def matrix_sum(matrix):
    total = 0
    for row in matrix:
        for cell in row:
            total += cell
    return total
        """
        
        try:
            unified_ast = self.ast_builder.build(code, SupportedLanguage.PYTHON)
            success = unified_ast is not None
            
            self._record_result(
                "Nested Loop Analysis",
                success,
                "AST built successfully with nested loops"
            )
            return success
        except Exception as e:
            self._record_result(
                "Nested Loop Analysis",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_complexity_analysis(self):
        """Test basic complexity analysis"""
        code = """
def linear_search(arr, target):
    for num in arr:
        if num == target:
            return True
    return False
        """
        
        try:
            unified_ast = self.ast_builder.build(code, SupportedLanguage.PYTHON)
            complexity_analyzer = ComplexityAnalyzer()
            
            # Parse metadata
            parsed = self.ast_builder.parsers[SupportedLanguage.PYTHON].parse(code)
            metadata = self.ast_builder.get_metadata(parsed)
            
            classical_complexity = complexity_analyzer.analyze(code, metadata, unified_ast)
            
            success = classical_complexity is not None
            
            self._record_result(
                "Complexity Analysis",
                success,
                f"Time: {classical_complexity.time_complexity}, Space: {classical_complexity.space_complexity}"
            )
            return success
        except Exception as e:
            self._record_result(
                "Complexity Analysis",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_qiskit_circuit_analysis(self):
        """Test Qiskit circuit analysis"""
        code = """
from qiskit import QuantumCircuit

qc = QuantumCircuit(3, 3)
qc.h(0)
qc.h(1)
qc.h(2)
qc.cx(0, 1)
qc.cx(1, 2)
qc.measure([0, 1, 2], [0, 1, 2])
        """
        
        try:
            unified_ast = self.ast_builder.build(code, SupportedLanguage.QISKIT)
            
            success = (unified_ast is not None and 
                      unified_ast.total_qubits > 0 and
                      unified_ast.total_gates > 0)
            
            self._record_result(
                "Qiskit Circuit Analysis",
                success,
                f"Qubits: {unified_ast.total_qubits}, Gates: {unified_ast.total_gates}"
            )
            return success
        except Exception as e:
            self._record_result(
                "Qiskit Circuit Analysis",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_ast_gate_extraction(self):
        """Test AST gate extraction"""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])
        """
        
        try:
            unified_ast = self.ast_builder.build(code, SupportedLanguage.QISKIT)
            
            # Check if gates were extracted
            success = len(unified_ast.gates) > 0
            
            self._record_result(
                "AST Gate Extraction",
                success,
                f"Gates extracted: {len(unified_ast.gates)}"
            )
            return success
        except Exception as e:
            self._record_result(
                "AST Gate Extraction",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_function_detection(self):
        """Test function detection"""
        code = """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

result = add(5, 3)
        """
        
        try:
            unified_ast = self.ast_builder.build(code, SupportedLanguage.PYTHON)
            
            success = unified_ast is not None and len(unified_ast.functions) > 0
            
            self._record_result(
                "Function Detection",
                success,
                f"Functions found: {len(unified_ast.functions)}"
            )
            return success
        except Exception as e:
            self._record_result(
                "Function Detection",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def test_conditional_analysis(self):
        """Test conditional statement analysis"""
        code = """
def classify(x):
    if x > 10:
        return "large"
    elif x > 5:
        return "medium"
    else:
        return "small"
        """
        
        try:
            unified_ast = self.ast_builder.build(code, SupportedLanguage.PYTHON)
            
            success = unified_ast is not None
            
            self._record_result(
                "Conditional Analysis",
                success,
                "AST built with conditionals"
            )
            return success
        except Exception as e:
            self._record_result(
                "Conditional Analysis",
                False,
                f"Error: {str(e)}"
            )
            return False
    
    def run_all_tests(self):
        """Run all regression tests"""
        print("\n" + "="*80)
        print("REGRESSION TEST SUITE")
        print("Verifying existing functionality is not broken")
        print("="*80 + "\n")
        
        tests = [
            self.test_python_language_detection,
            self.test_qiskit_language_detection,
            self.test_simple_loop_analysis,
            self.test_nested_loop_analysis,
            self.test_complexity_analysis,
            self.test_qiskit_circuit_analysis,
            self.test_ast_gate_extraction,
            self.test_function_detection,
            self.test_conditional_analysis,
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"CRITICAL ERROR in {test.__name__}: {str(e)}")
        
        self._print_summary()
    
    def _record_result(self, test_name: str, success: bool, details: str):
        """Record test result"""
        status = "PASS" if success else "FAIL"
        symbol = "[OK]" if success else "[XX]"
        
        print(f"{symbol} {test_name}")
        print(f"    {details}\n")
        
        self.results.append({
            "test_name": test_name,
            "passed": success,
            "details": details
        })
        
        if success:
            self.passed += 1
        else:
            self.failed += 1
    
    def _print_summary(self):
        """Print test summary"""
        total = len(self.results)
        print("\n" + "="*80)
        print("REGRESSION TEST SUMMARY")
        print("="*80)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed} [OK]")
        print(f"Failed: {self.failed} [XX]")
        print(f"Success Rate: {(self.passed/total*100):.1f}%")
        print("="*80)
        
        if self.failed > 0:
            print("\n[FAILED TESTS]")
            for result in self.results:
                if not result["passed"]:
                    print(f"  - {result['test_name']}: {result['details']}")
        
        self._save_results()
    
    def _save_results(self):
        """Save results to JSON"""
        output_file = os.path.join(
            os.path.dirname(__file__),
            "regression_test_results.json"
        )
        
        try:
            with open(output_file, 'w') as f:
                json.dump({
                    "total": len(self.results),
                    "passed": self.passed,
                    "failed": self.failed,
                    "success_rate": f"{(self.passed/len(self.results)*100):.1f}%",
                    "results": self.results
                }, f, indent=2)
            print(f"\n[Results saved to]: {output_file}")
        except Exception as e:
            print(f"[Warning] Could not save results: {e}")


if __name__ == "__main__":
    suite = RegressionTestSuite()
    suite.run_all_tests()
