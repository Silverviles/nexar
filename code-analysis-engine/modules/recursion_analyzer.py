"""
Unified Recursion Analyzer - Framework-Agnostic
Supports recursion analysis across Python, Qiskit, Cirq, Q#, and OpenQASM
"""
import ast
import re
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RecursionPattern(Enum):
    """Types of recursion patterns"""
    LINEAR = "linear"  # Single recursive call: O(n)
    BINARY = "binary"  # Two recursive calls: O(2^n)
    MULTIPLE = "multiple"  # Multiple recursive calls: O(k^n)
    DIVIDE_CONQUER = "divide_conquer"  # Divide and conquer: O(n*log(n))
    LOGARITHMIC = "logarithmic"  # Logarithmic: O(log(n))
    TAIL = "tail"  # Tail recursion: can be optimized
    MUTUAL = "mutual"  # Mutual recursion


class RecursionAnalyzer:
    """
    Framework-agnostic recursion analyzer
    Supports: Python (Qiskit, Cirq), Q#, and potentially others
    """
    
    def __init__(self):
        self.recursive_functions: Set[str] = set()
        self.call_graph: Dict[str, Set[str]] = {}
        self.recursion_patterns: Dict[str, RecursionPattern] = {}
        self.loop_counts: Dict[str, int] = {}
        self.recursion_depths: Dict[str, int] = {}
    
    def analyze_python_recursion(self, code: str) -> Dict:
        """Analyze recursion in Python code (for Qiskit, Cirq, etc.)"""
        try:
            tree = ast.parse(code)
            self._analyze_python_ast(tree)
            
            return {
                "recursive_functions": list(self.recursive_functions),
                "recursion_patterns": {k: v.value for k, v in self.recursion_patterns.items()},
                "call_graph": self.call_graph,
                "loop_counts": self.loop_counts,
                "recursion_depths": self.recursion_depths,
                "has_recursion": len(self.recursive_functions) > 0,
                "has_mutual_recursion": self._has_mutual_recursion()
            }
        except SyntaxError as e:
            logger.error(f"Syntax error in Python code: {e}")
            return self._empty_result()
    
    def analyze_qsharp_recursion(self, code: str) -> Dict:
        """Analyze recursion in Q# code"""
        try:
            self._analyze_qsharp_code(code)
            
            return {
                "recursive_functions": list(self.recursive_functions),
                "recursion_patterns": {k: v.value for k, v in self.recursion_patterns.items()},
                "call_graph": self.call_graph,
                "loop_counts": self.loop_counts,
                "recursion_depths": self.recursion_depths,
                "has_recursion": len(self.recursive_functions) > 0,
                "has_mutual_recursion": self._has_mutual_recursion()
            }
        except Exception as e:
            logger.error(f"Error analyzing Q# code: {e}")
            return self._empty_result()
    
    def _analyze_python_ast(self, tree: ast.AST, depth: int = 0) -> None:
        """Recursively analyze Python AST for recursion"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                self.call_graph[func_name] = set()
                self.loop_counts[func_name] = self._count_loops_python(node)
                
                # Check for direct recursion
                if self._has_direct_recursion(node):
                    self.recursive_functions.add(func_name)
                    pattern = self._detect_recursion_pattern(node)
                    self.recursion_patterns[func_name] = pattern
                    depth_val = self._calculate_recursion_depth_python(node)
                    self.recursion_depths[func_name] = depth_val
                
                # Build call graph
                for sub_node in ast.walk(node):
                    if isinstance(sub_node, ast.Call):
                        if isinstance(sub_node.func, ast.Name):
                            called_func = sub_node.func.id
                            self.call_graph[func_name].add(called_func)
    
    def _analyze_qsharp_code(self, code: str) -> None:
        """Analyze Q# code for recursion patterns"""
        lines = code.split('\n')
        
        # Pattern to find operations/functions
        operation_pattern = r'operation\s+(\w+)\s*\('
        
        current_operation = None
        current_operation_line = -1
        self.loop_counts = {}
        self.call_graph = {}
        
        for i, line in enumerate(lines):
            # Find operation definitions
            op_match = re.search(operation_pattern, line)
            if op_match:
                op_name = op_match.group(1)
                current_operation = op_name
                current_operation_line = i
                self.call_graph[op_name] = set()
                self.loop_counts[op_name] = 0
            
            # Find function calls within current operation
            if current_operation and i > current_operation_line:
                if 'for' in line.lower() or 'repeat' in line.lower():
                    self.loop_counts[current_operation] += 1
                
                # Look for recursive calls
                if re.search(rf'\b{re.escape(current_operation)}\s*\(', line):
                    self.recursive_functions.add(current_operation)
                    pattern = self._detect_qsharp_recursion_pattern(lines, current_operation)
                    self.recursion_patterns[current_operation] = pattern
    
    def _has_direct_recursion(self, func_node: ast.FunctionDef) -> bool:
        """Check if function directly calls itself"""
        func_name = func_node.name
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == func_name:
                    return True
        return False
    
    def _has_mutual_recursion(self) -> bool:
        """Check if there's mutual recursion in the call graph"""
        for func, called in self.call_graph.items():
            for c in called:
                if c in self.call_graph and func in self.call_graph.get(c, set()):
                    return True
        return False
    
    def _detect_recursion_pattern(self, func_node: ast.FunctionDef) -> RecursionPattern:
        """Detect recursion pattern in Python function"""
        # Count recursive calls
        call_count = 0
        has_division = False
        has_modulo = False
        has_tail_recursion = False
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == func_node.name:
                    call_count += 1
            
            if isinstance(node, (ast.BinOp)):
                if isinstance(node.op, (ast.Div, ast.FloorDiv)):
                    has_division = True
                elif isinstance(node.op, ast.Mod):
                    has_modulo = True
        
        # Check for tail recursion (recursive call is last operation in function)
        if func_node.body:
            last_node = func_node.body[-1]
            if isinstance(last_node, ast.Return):
                if isinstance(last_node.value, ast.Call):
                    if isinstance(last_node.value.func, ast.Name):
                        if last_node.value.func.id == func_node.name:
                            has_tail_recursion = True
        
        # Pattern detection logic
        if has_division and call_count == 2:
            return RecursionPattern.DIVIDE_CONQUER
        elif has_modulo and call_count == 1:
            return RecursionPattern.LOGARITHMIC
        elif has_tail_recursion:
            return RecursionPattern.TAIL
        elif call_count == 1:
            return RecursionPattern.LINEAR
        elif call_count == 2:
            return RecursionPattern.BINARY
        elif call_count > 2:
            return RecursionPattern.MULTIPLE
        
        return RecursionPattern.LINEAR
    
    def _detect_qsharp_recursion_pattern(self, lines: List[str], op_name: str) -> RecursionPattern:
        """Detect recursion pattern in Q# operation"""
        # Q# specific pattern detection
        # For now, assume linear recursion
        return RecursionPattern.LINEAR
    
    def _count_loops_python(self, node: ast.AST) -> int:
        """Count loops in Python AST node"""
        count = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.For, ast.While)):
                count += 1
        return count
    
    def _calculate_recursion_depth_python(self, func_node: ast.FunctionDef) -> int:
        """Calculate maximum recursion depth in Python function"""
        # Count recursive calls in single invocation
        call_count = 0
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == func_node.name:
                    call_count += 1
        
        # If more than one call, depth is number of branches
        return max(1, call_count)
    
    @staticmethod
    def _empty_result() -> Dict:
        """Return empty recursion analysis result"""
        return {
            "recursive_functions": [],
            "recursion_patterns": {},
            "call_graph": {},
            "loop_counts": {},
            "recursion_depths": {},
            "has_recursion": False,
            "has_mutual_recursion": False
        }
    
    def reset(self) -> None:
        """Reset analyzer state"""
        self.recursive_functions.clear()
        self.call_graph.clear()
        self.recursion_patterns.clear()
        self.loop_counts.clear()
        self.recursion_depths.clear()


# Helper functions for quick analysis
def analyze_recursion(code: str, language: str = "python") -> Dict:
    """
    Analyze recursion in code for given language
    
    Args:
        code: Source code to analyze
        language: Programming language ('python', 'qsharp', etc.)
    
    Returns:
        Dictionary with recursion analysis results
    """
    analyzer = RecursionAnalyzer()
    
    if language.lower() in ["python", "qiskit", "cirq"]:
        return analyzer.analyze_python_recursion(code)
    elif language.lower() == "qsharp":
        return analyzer.analyze_qsharp_recursion(code)
    else:
        logger.warning(f"Recursion analysis not supported for language: {language}")
        return RecursionAnalyzer._empty_result()


if __name__ == "__main__":
    # Test Python recursion
    python_code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
    """
    
    result = analyze_recursion(python_code, "python")
    print("Python Recursion Analysis:")
    print(f"  Recursive Functions: {result['recursive_functions']}")
    print(f"  Patterns: {result['recursion_patterns']}")
    print(f"  Has Mutual: {result['has_mutual_recursion']}")
