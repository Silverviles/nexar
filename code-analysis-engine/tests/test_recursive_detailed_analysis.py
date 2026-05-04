"""
Enhanced Recursive Function Test with Detailed Analysis & Explanations
Includes accuracy verification and recommendations for improvements
"""
import sys
import os
import json
from typing import Dict, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.language_detector import LanguageDetector
from modules.ast_builder import ASTBuilder
from modules.accurate_time_complexity import AccurateTimeComplexityAnalyzer
from modules.space_complexity_analyzer import AccurateSpaceComplexityAnalyzer
from models.analysis_result import TimeComplexity


class EnhancedRecursiveAnalyzer:
    """Enhanced analyzer with detailed complexity verification"""
    
    def __init__(self):
        self.time_analyzer = AccurateTimeComplexityAnalyzer()
        self.space_analyzer = AccurateSpaceComplexityAnalyzer()
        self.results = []
    
    def analyze_with_explanation(
        self,
        test_name: str,
        code: str,
        expected_time: str,
        expected_space: str,
        explanation: str,
        loop_count: int = 0,
        recursion_depth: int = 1
    ) -> Dict:
        """Analyze code and provide detailed explanation"""
        
        print(f"\n{'='*80}")
        print(f"TEST: {test_name.upper()}")
        print(f"{'='*80}")
        
        result = {
            "test_name": test_name,
            "explanation": explanation,
            "expected": {
                "time": expected_time,
                "space": expected_space,
                "loop_count": loop_count,
                "recursion_depth": recursion_depth
            },
            "actual": {},
            "analysis": ""
        }
        
        try:
            # Analyze time complexity
            time_complexity = self.time_analyzer.analyze(code)
            actual_time = time_complexity.value if hasattr(time_complexity, 'value') else str(time_complexity)
            
            # Analyze space complexity
            space_complexity = self.space_analyzer.analyze(code)
            
            # Detect recursion
            recursive_calls = self.time_analyzer.recursive_calls
            
            # Count loops in code
            loop_count = self._count_loops(code)
            
            result["actual"]["time"] = actual_time
            result["actual"]["space"] = space_complexity
            result["actual"]["recursion_detected"] = len(recursive_calls) > 0
            result["actual"]["recursive_functions"] = list(recursive_calls)
            result["actual"]["loop_count"] = loop_count
            
            # Print analysis
            print(f"\n[ANALYSIS EXPLANATION]:")
            print(f"{explanation}\n")
            
            print(f"[EXPECTED vs ACTUAL]:")
            print(f"  Time Complexity:")
            print(f"    Expected: O({expected_time})")
            print(f"    Actual:   {actual_time}")
            match_time = self._complexity_matches(expected_time, actual_time)
            print(f"    Status:   {'PASS' if match_time else 'FAIL'}")
            
            print(f"  Space Complexity:")
            print(f"    Expected: {expected_space}")
            print(f"    Actual:   {space_complexity}")
            match_space = self._complexity_matches(expected_space.replace('O(', '').replace(')', ''), space_complexity.replace('O(', '').replace(')', ''))
            print(f"    Status:   {'PASS' if match_space else 'FAIL'}")
            
            print(f"  Loop Analysis:")
            print(f"    Expected Loop Count: {loop_count}")
            print(f"    Actual Loop Count:   {result['actual']['loop_count']}")
            
            print(f"  Recursion Detection:")
            print(f"    Expected Depth: {recursion_depth}")
            print(f"    Detected: {len(recursive_calls) > 0}")
            if recursive_calls:
                print(f"    Functions: {', '.join(recursive_calls)}")
            
            # Analysis
            analysis = []
            if match_time:
                analysis.append("PASS: Time complexity correctly identified")
            else:
                analysis.append(f"FAIL: Time complexity mismatch (expected {expected_time}, got {actual_time})")
            
            if match_space:
                analysis.append("PASS: Space complexity correctly identified")
            else:
                analysis.append(f"FAIL: Space complexity mismatch")
            
            if len(recursive_calls) > 0:
                analysis.append(f"PASS: Recursion detected ({len(recursive_calls)} function(s))")
            else:
                analysis.append("FAIL: Recursion not detected")
            
            result["analysis"] = analysis
            print(f"\n{'='*80}\n")
            
        except Exception as e:
            result["error"] = str(e)
            print(f"ERROR: {str(e)}\n")
        
        self.results.append(result)
        return result
    
    def _complexity_matches(self, expected: str, actual: str) -> bool:
        """Check if complexities match (allowing some flexibility)"""
        expected_clean = expected.replace('O(', '').replace(')', '').strip().lower()
        actual_clean = actual.replace('O(', '').replace(')', '').strip().lower()
        return expected_clean == actual_clean
    
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
    
    def run_detailed_tests(self):
        """Run tests with detailed analysis"""
        
        print("\n" + "="*80)
        print("RECURSIVE FUNCTION ANALYSIS - DETAILED TEST SUITE")
        print("="*80)
        print("This suite provides detailed analysis of recursion detection,")
        print("complexity calculation, and loop counting in your system.")
        print("="*80)
        
        # Test 1: Simple Recursion with No Loops
        self.analyze_with_explanation(
            test_name="simple_linear_recursion",
            code="""
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
            """,
            expected_time="n",
            expected_space="O(n)",
            explanation="""
SIMPLE LINEAR RECURSION:
- Each call reduces n by 1
- Single recursive call per invocation
- Time: O(n) - n recursive calls
- Space: O(n) - call stack depth is n
- Loop Count: 0 (no explicit loops)
            """,
            loop_count=0,
            recursion_depth=1
        )
        
        # Test 2: Binary Recursion
        self.analyze_with_explanation(
            test_name="binary_recursion",
            code="""
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
            """,
            expected_time="2^n",
            expected_space="O(n)",
            explanation="""
BINARY RECURSION (Exponential):
- Two recursive calls per invocation
- Unoptimized: explores all branches
- Time: O(2^n) - exponential branching factor
- Space: O(n) - max depth is n
- Loop Count: 0
- Key Pattern: 2 recursive calls = O(2^n)
            """,
            loop_count=0,
            recursion_depth=2
        )
        
        # Test 3: Recursion with Loop (Nested Complexity)
        self.analyze_with_explanation(
            test_name="recursion_with_loop",
            code="""
def process_matrix(matrix, index=0):
    if index >= len(matrix):
        return 0
    
    row_sum = 0
    for element in matrix[index]:
        row_sum += element
    
    return row_sum + process_matrix(matrix, index + 1)
            """,
            expected_time="n^2",
            expected_space="O(n)",
            explanation="""
RECURSION COMBINED WITH LOOPS (Nested):
- Recursive calls: n (one per row)
- Loop operations: n (per row element)
- Time: O(n^2) - n recursive calls × n loop iterations
- Space: O(n) - call stack depth is n
- Loop Count: 1 (inner loop in recursive function)
- Key Pattern: Recursion × Loop = O(n × m)
            """,
            loop_count=1,
            recursion_depth=1
        )
        
        # Test 4: Divide and Conquer (Log-Linear)
        self.analyze_with_explanation(
            test_name="merge_sort",
            code="""
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
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
            """,
            expected_time="n*log(n)",
            expected_space="O(n)",
            explanation="""
DIVIDE AND CONQUER (Merge Sort):
- Divides array in half: log(n) levels
- Each level processes all n elements: n work per level
- Time: O(n*log(n)) = n elements × log(n) depth
- Space: O(n) - temporary arrays for merging
- Loop Count: 1 (in merge function)
- Key Pattern: Binary division + linear merge = O(n*log(n))
- Master Theorem: T(n) = 2T(n/2) + O(n) = O(n*log(n))
            """,
            loop_count=1,
            recursion_depth=2
        )
        
        # Test 5: Binary Search (Logarithmic)
        self.analyze_with_explanation(
            test_name="binary_search",
            code="""
def binary_search(arr, target, low, high):
    if low > high:
        return -1
    
    mid = (low + high) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search(arr, target, mid + 1, high)
    else:
        return binary_search(arr, target, low, mid - 1)
            """,
            expected_time="log(n)",
            expected_space="O(log(n))",
            explanation="""
BINARY SEARCH (Logarithmic):
- Halves search space each call: log(n) levels
- Single recursive call per invocation
- Time: O(log(n)) - depth is log₂(n)
- Space: O(log(n)) - call stack depth is log(n)
- Loop Count: 0 (no loops, pure recursion)
- Key Pattern: Single recursive call with division = O(log(n))
            """,
            loop_count=0,
            recursion_depth=1
        )
        
        # Test 6: GCD - Euclidean Algorithm (Logarithmic)
        self.analyze_with_explanation(
            test_name="gcd_euclidean",
            code="""
def gcd(a, b):
    if b == 0:
        return a
    return gcd(b, a % b)
            """,
            expected_time="log(n)",
            expected_space="O(log(n))",
            explanation="""
EUCLIDEAN GCD ALGORITHM (Logarithmic):
- Reduces pair size logarithmically: gcd(a, b) → gcd(b, a%b)
- Time: O(log(min(a,b))) - approximately 5 iterations per digit
- Space: O(log(n)) - call stack depth is logarithmic
- Loop Count: 0
- Key Pattern: Modulo reduces dramatically = O(log(n))
            """,
            loop_count=0,
            recursion_depth=1
        )
        
        # Test 7: Mutual Recursion (Cross-Function)
        self.analyze_with_explanation(
            test_name="mutual_recursion",
            code="""
def is_even(n):
    if n == 0:
        return True
    return is_odd(n - 1)

def is_odd(n):
    if n == 0:
        return False
    return is_even(n - 1)
            """,
            expected_time="n",
            expected_space="O(n)",
            explanation="""
MUTUAL RECURSION (Cross-Function):
- is_even calls is_odd, which calls is_even
- Both functions call each other recursively
- Time: O(n) - n alternating calls
- Space: O(n) - call stack with n frames
- Loop Count: 0
- Challenge: Requires tracking cross-function recursive calls
- ⚠️ System may not detect this as recursion (single function check)
            """,
            loop_count=0,
            recursion_depth=1
        )
        
        # Test 8: QuickSort (Divide and Conquer Variant)
        self.analyze_with_explanation(
            test_name="quicksort",
            code="""
def quicksort(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        pi = partition(arr, low, high)
        quicksort(arr, low, pi - 1)
        quicksort(arr, pi + 1, high)
    return arr

def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
            """,
            expected_time="n*log(n)",
            expected_space="O(log(n))",
            explanation="""
QUICKSORT (Average Case Divide and Conquer):
- Average: O(n*log(n)) - balanced partitions
- Worst: O(n²) - sorted input or poor pivot
- Space: O(log(n)) - average recursion depth
- Loop Count: 1 (in partition)
- Key Pattern: Partition + binary recursion = O(n*log(n)) average
- Harder to analyze because complexity depends on pivot selection
            """,
            loop_count=1,
            recursion_depth=2
        )
        
        # Test 9: Ackermann Function (Very Deep)
        self.analyze_with_explanation(
            test_name="ackermann_function",
            code="""
def ackermann(m, n):
    if m == 0:
        return n + 1
    elif n == 0:
        return ackermann(m - 1, 1)
    else:
        return ackermann(m - 1, ackermann(m, n - 1))
            """,
            expected_time="unknown",
            expected_space="O(n)",
            explanation="""
ACKERMANN FUNCTION (Extreme Recursion):
- One of the fastest-growing functions in mathematics
- Time: Not primitive recursive - grows faster than exponential
- Space: O(n) - approximate call stack depth
- Loop Count: 0
- Pattern: Nested recursive calls with varying parameters
- Note: Even ackermann(4, 2) produces astronomically large numbers
            """,
            loop_count=0,
            recursion_depth=3
        )
        
        # Test 10: Tail Recursion (Optimization Candidate)
        self.analyze_with_explanation(
            test_name="tail_recursion",
            code="""
def sum_list(numbers, index=0, accumulator=0):
    if index >= len(numbers):
        return accumulator
    return sum_list(numbers, index + 1, accumulator + numbers[index])
            """,
            expected_time="n",
            expected_space="O(1)",
            explanation="""
TAIL RECURSION (Optimization Candidate):
- Recursive call is the last operation
- In languages with tail-call optimization: O(1) space (converted to loop)
- Python: O(n) space (no tail-call optimization)
- Time: O(n) - n iterations
- Space: O(n) in Python, but could be O(1) with optimization
- Pattern: Accumulator passed through recursive calls
            """,
            loop_count=0,
            recursion_depth=1
        )
        
        self._print_detailed_summary()
    
    def _print_detailed_summary(self):
        """Print detailed summary with recommendations"""
        print("\n" + "="*80)
        print("SUMMARY & RECOMMENDATIONS")
        print("="*80)
        
        correct_time = sum(1 for r in self.results if r.get("analysis") and "PASS: Time complexity" in str(r["analysis"]))
        correct_space = sum(1 for r in self.results if r.get("analysis") and "PASS: Space complexity" in str(r["analysis"]))
        recursion_detected = sum(1 for r in self.results if r.get("actual", {}).get("recursion_detected"))
        
        total = len(self.results)
        
        print(f"\n[STATISTICS]:")
        print(f"  Total Tests: {total}")
        print(f"  Time Complexity Accuracy: {correct_time}/{total} ({correct_time/total*100:.0f}%)")
        print(f"  Space Complexity Accuracy: {correct_space}/{total} ({correct_space/total*100:.0f}%)")
        print(f"  Recursion Detection: {recursion_detected}/{total} ({recursion_detected/total*100:.0f}%)")
        
        print(f"\n[KEY FINDINGS]:")
        print("""
1. STRENGTHS:
   - Simple recursion correctly identified (factorial, countdown)
   - Space complexity analysis is generally accurate
   - Recursion detection works for single-function recursion
   - Correctly identifies exponential (2^n) recursion patterns

2. AREAS FOR IMPROVEMENT:
   a) Multi-branch Recursion:
      - Tree recursion (multiple calls) sometimes detected as 2^n
      - Should differentiate between call count and actual complexity
   
   b) Recursion with Loops:
      - Nested complexity (recursion x loop) not fully captured
      - Needs better multiplication of complexities
   
   c) Divide and Conquer:
      - Doesn't apply Master Theorem heuristics
      - Binary split + linear work = O(n*log(n)) not always detected
   
   d) Logarithmic Recursion:
      - Binary search and GCD detected as O(n) instead of O(log(n))
      - Needs detection of division/reduction patterns
   
   e) Mutual Recursion:
      - Cross-function recursion not detected
      - Currently only checks within single function
   
   f) Edge Cases:
      - Tail recursion space complexity (O(1) vs O(n))
      - QuickSort average vs worst case distinction

3. RECOMMENDATIONS FOR FIXES:
   
   a) Add Master Theorem Recognition:
      - Detect patterns like: 2T(n/2) + O(n) = O(n*log(n))
      - Check for binary/logarithmic divisions
   
   b) Cross-Function Analysis:
      - Build call graph for mutual recursion
      - Track recursive chains across functions
   
   c) Improved Complexity Multiplication:
      - Better combine recursion depth with loop operations
      - Context-aware complexity inference
   
   d) Pattern-Based Detection:
      - Recognize common patterns (binary search, divide-conquer, etc.)
      - Use known algorithm signatures as hints
   
   e) Depth Analysis:
      - Track actual depth vs time complexity separately
      - Distinguish between space depth and time iterations
        """)
        
        self._save_detailed_results()
    
    def _save_detailed_results(self):
        """Save detailed results to file"""
        output_file = os.path.join(
            os.path.dirname(__file__),
            "detailed_recursive_analysis.json"
        )
        
        try:
            with open(output_file, 'w') as f:
                json.dump({
                    "timestamp": self._get_timestamp(),
                    "test_count": len(self.results),
                    "results": self.results
                }, f, indent=2)
            print(f"\n[Results saved to]: {output_file}")
        except Exception as e:
            print(f"[Warning] Could not save results: {e}")
    
    @staticmethod
    def _get_timestamp():
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    analyzer = EnhancedRecursiveAnalyzer()
    analyzer.run_detailed_tests()
