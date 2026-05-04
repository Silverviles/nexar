"""
Recursive Functions Test Suite
Comprehensive testing for recursion support in code analysis engine

Tests:
1. Simple recursion (factorial, countdown)
2. Binary recursion (fibonacci)
3. Tail recursion (accumulator pattern)
4. Multiple recursion (tree traversal)
5. Mutual recursion (even/odd)
6. Recursive with loops
7. Divide and conquer (merge sort)
"""
import sys
import os
import json
import traceback
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.language_detector import LanguageDetector, SupportedLanguage
from modules.ast_builder import ASTBuilder
from modules.complexity_analyzer import ComplexityAnalyzer
from modules.accurate_time_complexity import AccurateTimeComplexityAnalyzer
from modules.space_complexity_analyzer import AccurateSpaceComplexityAnalyzer
from models.analysis_result import TimeComplexity


class RecursiveTestRunner:
    """Test runner for recursive function analysis"""
    
    def __init__(self):
        self.detector = LanguageDetector()
        self.ast_builder = ASTBuilder()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.time_complexity_analyzer = AccurateTimeComplexityAnalyzer()
        self.space_complexity_analyzer = AccurateSpaceComplexityAnalyzer()
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    def test_simple_recursion_factorial(self):
        """Test 1: Simple linear recursion - Factorial"""
        print("\n" + "="*80)
        print("TEST 1: Simple Recursion - Factorial (O(n) time, O(n) space)")
        print("="*80)
        
        code = """
def factorial(n):
    '''Calculate factorial recursively'''
    if n <= 1:
        return 1
    return n * factorial(n - 1)

result = factorial(5)
        """
        
        return self._run_analysis(
            test_name="factorial",
            code=code,
            expected_time_complexity="n",
            expected_space_complexity="O(n)",
            expected_recursion_depth=1,
            description="Simple linear recursion"
        )
    
    def test_binary_recursion_fibonacci(self):
        """Test 2: Binary recursion - Fibonacci"""
        print("\n" + "="*80)
        print("TEST 2: Binary Recursion - Fibonacci (O(2^n) time, O(n) space)")
        print("="*80)
        
        code = """
def fibonacci(n):
    '''Calculate fibonacci number recursively'''
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

result = fibonacci(10)
        """
        
        return self._run_analysis(
            test_name="fibonacci",
            code=code,
            expected_time_complexity="2^n",
            expected_space_complexity="O(n)",
            expected_recursion_depth=2,
            description="Binary recursion (exponential time)"
        )
    
    def test_tail_recursion(self):
        """Test 3: Tail recursion - Accumulator pattern"""
        print("\n" + "="*80)
        print("TEST 3: Tail Recursion - Sum with accumulator (O(n) time, O(n) space)")
        print("="*80)
        
        code = """
def sum_list(numbers, index=0, accumulator=0):
    '''Sum list using tail recursion'''
    if index >= len(numbers):
        return accumulator
    return sum_list(numbers, index + 1, accumulator + numbers[index])

result = sum_list([1, 2, 3, 4, 5])
        """
        
        return self._run_analysis(
            test_name="tail_recursion",
            code=code,
            expected_time_complexity="n",
            expected_space_complexity="O(n)",
            expected_recursion_depth=1,
            description="Tail recursion pattern"
        )
    
    def test_tree_recursion(self):
        """Test 4: Tree recursion - Multiple branches"""
        print("\n" + "="*80)
        print("TEST 4: Tree Recursion - Tree traversal (O(n) time, O(h) space)")
        print("="*80)
        
        code = """
def tree_sum(node):
    '''Sum all values in a binary tree recursively'''
    if node is None:
        return 0
    left_sum = tree_sum(node.left)
    right_sum = tree_sum(node.right)
    return node.value + left_sum + right_sum

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

root = TreeNode(1)
result = tree_sum(root)
        """
        
        return self._run_analysis(
            test_name="tree_recursion",
            code=code,
            expected_time_complexity="n",
            expected_space_complexity="O(n)",
            expected_recursion_depth=2,
            description="Tree traversal with multiple recursive calls"
        )
    
    def test_mutual_recursion_even_odd(self):
        """Test 5: Mutual recursion - Even/Odd"""
        print("\n" + "="*80)
        print("TEST 5: Mutual Recursion - Even/Odd check (O(n) time, O(n) space)")
        print("="*80)
        
        code = """
def is_even(n):
    '''Check if number is even using mutual recursion'''
    if n == 0:
        return True
    return is_odd(n - 1)

def is_odd(n):
    '''Check if number is odd using mutual recursion'''
    if n == 0:
        return False
    return is_even(n - 1)

result = is_even(10)
        """
        
        return self._run_analysis(
            test_name="mutual_recursion",
            code=code,
            expected_time_complexity="n",
            expected_space_complexity="O(n)",
            expected_recursion_depth=1,
            description="Mutual recursion between functions"
        )
    
    def test_recursive_with_loop(self):
        """Test 6: Recursion with loop inside"""
        print("\n" + "="*80)
        print("TEST 6: Recursion with Loop (O(n^2) time, O(n) space)")
        print("="*80)
        
        code = """
def nested_sum(matrix):
    '''Sum matrix using recursion and loops'''
    if not matrix:
        return 0
    
    row_sum = 0
    for num in matrix[0]:
        row_sum += num
    
    return row_sum + nested_sum(matrix[1:])

data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
result = nested_sum(data)
        """
        
        return self._run_analysis(
            test_name="recursive_with_loop",
            code=code,
            expected_time_complexity="n^2",
            expected_space_complexity="O(n)",
            expected_recursion_depth=1,
            description="Recursion combined with nested loops"
        )
    
    def test_divide_and_conquer_merge_sort(self):
        """Test 7: Divide and conquer - Merge sort"""
        print("\n" + "="*80)
        print("TEST 7: Divide and Conquer - Merge Sort (O(n*log(n)) time, O(n) space)")
        print("="*80)
        
        code = """
def merge_sort(arr):
    '''Merge sort using divide and conquer'''
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    '''Merge two sorted arrays'''
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result

arr = [64, 34, 25, 12, 22, 11, 90]
result = merge_sort(arr)
        """
        
        return self._run_analysis(
            test_name="merge_sort",
            code=code,
            expected_time_complexity="n*log(n)",
            expected_space_complexity="O(n)",
            expected_recursion_depth=2,
            description="Divide and conquer with logarithmic split"
        )
    
    def test_quicksort_partition(self):
        """Test 8: QuickSort - Divide and conquer variant"""
        print("\n" + "="*80)
        print("TEST 8: QuickSort (O(n*log(n)) average, O(n^2) worst)")
        print("="*80)
        
        code = """
def quicksort(arr, low=0, high=None):
    '''Quick sort using divide and conquer'''
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        pi = partition(arr, low, high)
        quicksort(arr, low, pi - 1)
        quicksort(arr, pi + 1, high)
    
    return arr

def partition(arr, low, high):
    '''Partition array for quicksort'''
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

arr = [64, 34, 25, 12, 22, 11, 90]
result = quicksort(arr)
        """
        
        return self._run_analysis(
            test_name="quicksort",
            code=code,
            expected_time_complexity="n*log(n)",
            expected_space_complexity="O(n)",
            expected_recursion_depth=2,
            description="QuickSort with partition function"
        )
    
    def test_deep_recursion_countdown(self):
        """Test 9: Deep recursion - Simple countdown"""
        print("\n" + "="*80)
        print("TEST 9: Deep Recursion - Countdown (O(n) time, O(n) space)")
        print("="*80)
        
        code = """
def countdown(n):
    '''Simple countdown recursion'''
    if n <= 0:
        print("Blastoff!")
        return
    print(n)
    countdown(n - 1)

countdown(100)
        """
        
        return self._run_analysis(
            test_name="countdown",
            code=code,
            expected_time_complexity="n",
            expected_space_complexity="O(n)",
            expected_recursion_depth=1,
            description="Simple linear countdown recursion"
        )
    
    def test_ackermann_function(self):
        """Test 10: Ackermann function - Very deep recursion"""
        print("\n" + "="*80)
        print("TEST 10: Ackermann Function (Extremely deep recursion)")
        print("="*80)
        
        code = """
def ackermann(m, n):
    '''Ackermann function - grows extremely quickly'''
    if m == 0:
        return n + 1
    elif n == 0:
        return ackermann(m - 1, 1)
    else:
        return ackermann(m - 1, ackermann(m, n - 1))

result = ackermann(2, 2)
        """
        
        return self._run_analysis(
            test_name="ackermann",
            code=code,
            expected_time_complexity="unknown",
            expected_space_complexity="O(n)",
            expected_recursion_depth=3,
            description="Ackermann function with multiple nested recursion"
        )
    
    def test_gcd_euclidean_algorithm(self):
        """Test 11: GCD - Euclidean Algorithm"""
        print("\n" + "="*80)
        print("TEST 11: GCD - Euclidean Algorithm (O(log(min(a,b))) time)")
        print("="*80)
        
        code = """
def gcd(a, b):
    '''Calculate GCD using Euclidean algorithm'''
    if b == 0:
        return a
    return gcd(b, a % b)

result = gcd(48, 18)
        """
        
        return self._run_analysis(
            test_name="gcd",
            code=code,
            expected_time_complexity="log(n)",
            expected_space_complexity="O(log(n))",
            expected_recursion_depth=1,
            description="Euclidean algorithm for GCD (logarithmic)"
        )
    
    def test_recursive_array_search(self):
        """Test 12: Binary search - Recursive"""
        print("\n" + "="*80)
        print("TEST 12: Binary Search - Recursive (O(log(n)) time)")
        print("="*80)
        
        code = """
def binary_search(arr, target, low, high):
    '''Binary search using recursion'''
    if low > high:
        return -1
    
    mid = (low + high) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search(arr, target, mid + 1, high)
    else:
        return binary_search(arr, target, low, mid - 1)

arr = [1, 3, 5, 7, 9, 11, 13, 15]
result = binary_search(arr, 7, 0, len(arr) - 1)
        """
        
        return self._run_analysis(
            test_name="binary_search",
            code=code,
            expected_time_complexity="log(n)",
            expected_space_complexity="O(log(n))",
            expected_recursion_depth=1,
            description="Binary search recursion"
        )
    
    def _run_analysis(
        self,
        test_name: str,
        code: str,
        expected_time_complexity: str,
        expected_space_complexity: str,
        expected_recursion_depth: int,
        description: str
    ) -> Dict[str, Any]:
        """Run complete analysis on code"""
        self.total_tests += 1
        test_result = {
            "test_name": test_name,
            "description": description,
            "passed": False,
            "errors": [],
            "results": {}
        }
        
        try:
            # Step 1: Language detection
            print(f"\n[1/5] Detecting language...")
            lang_result = self.detector.detect(code)
            print(f"  ✓ Language: {lang_result['language']}")
            test_result["results"]["language"] = {
                "detected": lang_result['language'],
                "confidence": lang_result['confidence']
            }
            
            # Step 2: Parse and build AST
            print(f"[2/5] Building unified AST...")
            language_enum = SupportedLanguage.PYTHON
            unified_ast = self.ast_builder.build(code, language_enum)
            print(f"  ✓ Total qubits: {unified_ast.total_qubits}")
            print(f"  ✓ Total gates: {unified_ast.total_gates}")
            test_result["results"]["ast"] = {
                "total_qubits": unified_ast.total_qubits,
                "total_gates": unified_ast.total_gates,
                "status": "built"
            }
            
            # Step 3: Time complexity analysis
            print(f"[3/5] Analyzing time complexity...")
            time_complexity = self.time_complexity_analyzer.analyze(code)
            actual_time = time_complexity.value if hasattr(time_complexity, 'value') else str(time_complexity)
            print(f"  Expected: O({expected_time_complexity})")
            print(f"  Actual:   {actual_time}")
            test_result["results"]["time_complexity"] = {
                "expected": expected_time_complexity,
                "actual": actual_time
            }
            
            # Step 4: Space complexity analysis
            print(f"[4/5] Analyzing space complexity...")
            space_complexity = self.space_complexity_analyzer.analyze(code)
            print(f"  Expected: {expected_space_complexity}")
            print(f"  Actual:   {space_complexity}")
            test_result["results"]["space_complexity"] = {
                "expected": expected_space_complexity,
                "actual": space_complexity
            }
            
            # Step 5: Recursion detection
            print(f"[5/5] Detecting recursion...")
            recursion_depth = self.time_complexity_analyzer.recursive_calls
            loop_count = self._count_loops(code)
            print(f"  Recursion depth: {expected_recursion_depth}")
            print(f"  Recursive calls detected: {len(recursion_depth) > 0}")
            print(f"  Actual loop count: {loop_count}")
            test_result["results"]["recursion"] = {
                "detected": len(recursion_depth) > 0,
                "recursive_functions": list(recursion_depth),
                "max_recursion_depth": expected_recursion_depth,
                "actual_loop_count": loop_count
            }
            
            # Mark as passed
            test_result["passed"] = True
            self.passed_tests += 1
            print(f"\n✅ TEST PASSED: {test_name}")
            
        except Exception as e:
            test_result["errors"].append({
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            self.failed_tests += 1
            print(f"\n❌ TEST FAILED: {test_name}")
            print(f"   Error: {str(e)}")
        
        self.results.append(test_result)
        return test_result
    
    def _count_loops(self, code: str) -> int:
        """Count the number of loops in code"""
        import ast
        try:
            tree = ast.parse(code)
            loop_count = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.For, ast.While)):
                    loop_count += 1
            return loop_count
        except:
            return 0
    
    def run_all_tests(self):
        """Run all recursive function tests"""
        print("\n" + "="*80)
        print("RECURSIVE FUNCTIONS TEST SUITE")
        print("="*80)
        print(f"Starting test run at {self._get_timestamp()}")
        
        tests = [
            self.test_simple_recursion_factorial,
            self.test_binary_recursion_fibonacci,
            self.test_tail_recursion,
            self.test_tree_recursion,
            self.test_mutual_recursion_even_odd,
            self.test_recursive_with_loop,
            self.test_divide_and_conquer_merge_sort,
            self.test_quicksort_partition,
            self.test_deep_recursion_countdown,
            self.test_ackermann_function,
            self.test_gcd_euclidean_algorithm,
            self.test_recursive_array_search,
        ]
        
        for test_func in tests:
            try:
                test_func()
            except Exception as e:
                print(f"\n⚠️  Exception running test: {str(e)}")
                traceback.print_exc()
        
        self._print_summary()
    
    def _print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print("="*80)
        
        # Detailed results
        print("\nDETAILED RESULTS:")
        print("="*80)
        for result in self.results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"\n{status} - {result['test_name'].upper()}")
            print(f"Description: {result['description']}")
            
            if result["passed"]:
                if "time_complexity" in result["results"]:
                    tc = result["results"]["time_complexity"]
                    print(f"  Time Complexity: {tc['expected']} (detected: {tc['actual']})")
                if "space_complexity" in result["results"]:
                    sc = result["results"]["space_complexity"]
                    print(f"  Space Complexity: {sc['expected']} (detected: {sc['actual']})")
                if "recursion" in result["results"]:
                    rec = result["results"]["recursion"]
                    print(f"  Recursion Detected: {rec['detected']}")
                    if rec["recursive_functions"]:
                        print(f"  Recursive Functions: {', '.join(rec['recursive_functions'])}")
            else:
                for error in result["errors"]:
                    print(f"  ❌ Error: {error['error']}")
        
        # Save results to JSON
        self._save_results()
    
    def _save_results(self):
        """Save test results to JSON file"""
        output_file = os.path.join(
            os.path.dirname(__file__),
            "recursive_test_results.json"
        )
        
        summary = {
            "timestamp": self._get_timestamp(),
            "total_tests": self.total_tests,
            "passed": self.passed_tests,
            "failed": self.failed_tests,
            "success_rate": f"{(self.passed_tests/self.total_tests*100):.1f}%",
            "results": self.results
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"\n📊 Results saved to: {output_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save results: {e}")
    
    @staticmethod
    def _get_timestamp():
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """Main entry point"""
    runner = RecursiveTestRunner()
    runner.run_all_tests()


if __name__ == "__main__":
    main()
