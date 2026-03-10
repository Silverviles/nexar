"""
Accurate Time Complexity Analysis using AST and Data Flow
"""
import ast
import logging
from typing import Dict, Set, Optional
from models.analysis_result import TimeComplexity

logger = logging.getLogger(__name__)

class AccurateTimeComplexityAnalyzer:
    """Analyzes time complexity through AST traversal and loop bound analysis"""
    
    def __init__(self):
        self.loop_bounds = {}
        self.recursive_calls = set()
        self.has_heap_usage = False
        self.has_graph_search_pattern = False
    
    def analyze(self, code: str) -> TimeComplexity:
        """
        Analyze time complexity accurately through AST analysis
        """
        try:
            self.recursive_calls.clear()
            tree = ast.parse(code)
            self._collect_context(tree)
            complexity = self._analyze_node(tree)
            if self.has_heap_usage and self.has_graph_search_pattern and complexity in {'n^2', 'n^3'}:
                # A*/Dijkstra-like pattern: priority queue frontier + graph-style expansion.
                complexity = 'n*log(n)'
            result = self._complexity_to_enum(complexity)
            logger.debug("Time complexity analysis result: %s (raw=%s)", result.value, complexity)
            return result
        except SyntaxError:
            logger.warning("SyntaxError during time complexity analysis, returning UNKNOWN")
            return TimeComplexity.UNKNOWN
    
    def _analyze_node(self, node: ast.AST, depth: int = 0) -> str:
        """
        Recursively analyze AST nodes
        Returns: complexity string like 'n', 'n^2', 'log(n)', etc.
        """
        if isinstance(node, ast.Module):
            # Analyze all top-level statements
            complexities = [self._analyze_node(child, depth) for child in node.body]
            return self._max_complexity(complexities)
        
        elif isinstance(node, ast.FunctionDef):
            # Check for recursion
            self._check_recursion(node)
            
            # Analyze **all statements** in the function body
            body_complexities = [self._analyze_node(child, depth) for child in node.body]
            body_complexity = self._max_complexity(body_complexities)
            
            if node.name in self.recursive_calls:
                return self._analyze_recursion(node)
            
            return body_complexity
        
        elif isinstance(node, ast.For):
            # Analyze loop bounds
            loop_bound = self._get_loop_bound(node)
            body_complexity = self._max_complexity(
                [self._analyze_node(child, depth + 1) for child in node.body]
            )
            return self._multiply_complexity(loop_bound, body_complexity)
        
        elif isinstance(node, ast.While):
            # Conservative: assume O(n) unless proven otherwise
            body_complexity = self._max_complexity(
                [self._analyze_node(child, depth + 1) for child in node.body]
            )
            return self._multiply_complexity('n', body_complexity)
        
        elif isinstance(node, (list, ast.If)):
            # Analyze branches/sequences, take maximum
            if isinstance(node, list):
                items = node
            else:
                items = node.body + node.orelse
            
            complexities = [self._analyze_node(child, depth) for child in items]
            return self._max_complexity(complexities)
        
        elif isinstance(node, ast.Call):
            # Check for built-in operations
            if isinstance(node.func, ast.Name):
                return self._get_builtin_complexity(node.func.id)
            if isinstance(node.func, ast.Attribute):
                return self._get_builtin_complexity(node.func.attr)
            return '1'
        
        else:
            # Default: constant time
            return '1'
    
    def _get_loop_bound(self, node: ast.For) -> str:
        """
        Determine loop iteration count
        """
        # Check for range(n), range(len(array)), etc.
        if isinstance(node.iter, ast.Call):
            if isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range':
                args = node.iter.args
                if len(args) == 1:
                    # range(n) or range(len(x))
                    if isinstance(args[0], ast.Call) and isinstance(args[0].func, ast.Name):
                        if args[0].func.id == 'len':
                            return 'n'  # O(n)
                    elif isinstance(args[0], ast.Name):
                        return 'n'  # O(n)
                    elif isinstance(args[0], ast.Constant):
                        return str(args[0].value)  # O(k) constant
        
        # Default: assume O(n)
        return 'n'
    
    def _check_recursion(self, func_node: ast.FunctionDef):
        """Check if function calls itself"""
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == func_node.name:
                    self.recursive_calls.add(func_node.name)
    
    def _analyze_recursion(self, func_node: ast.FunctionDef) -> str:
        """
        Analyze recursive function complexity
        Uses Master Theorem heuristics
        """
        # Count recursive calls
        call_count = 0
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == func_node.name:
                    call_count += 1
        
        # Heuristic patterns
        if call_count == 1:
            return 'n'  # Linear recursion (e.g., factorial)
        elif call_count == 2:
            # Check for divide-and-conquer pattern
            has_division = any(
                isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div)
                for n in ast.walk(func_node)
            )
            if has_division:
                return 'n*log(n)'  # Merge sort, quick sort
            else:
                return '2^n'  # Fibonacci-like
        elif call_count >= 3:
            return 'n!'  # Permutation-like
        
        return 'n'
    
    def _multiply_complexity(self, bound: str, inner: str) -> str:
        """Multiply complexities (nested loops)"""
        if bound == '1':
            return inner
        if inner == '1':
            return bound
        
        # Simplify common cases
        if bound == 'n' and inner == 'n':
            return 'n^2'
        if bound == 'n' and inner == 'n^2':
            return 'n^3'
        if bound == 'n' and inner == 'log(n)':
            return 'n*log(n)'
        if bound == 'log(n)' and inner == 'n':
            return 'n*log(n)'
        
        # Default: concatenate
        return f"{bound}*{inner}"
    
    def _max_complexity(self, complexities: list) -> str:
        """Return dominant (maximum) complexity"""
        if not complexities:
            return '1'
        
        # Order of dominance
        order = ['1', 'log(n)', 'n', 'n*log(n)', 'n^2', 'n^3', '2^n', 'n!']
        
        max_comp = '1'
        for comp in complexities:
            if comp in order:
                if order.index(comp) > order.index(max_comp):
                    max_comp = comp
        
        return max_comp
    
    def _get_builtin_complexity(self, func_name: str) -> str:
        """Known complexity of built-in functions"""
        complexities = {
            'sorted': 'n*log(n)',
            'sort': 'n*log(n)',
            'min': 'n',
            'max': 'n',
            'sum': 'n',
            'len': '1',
            'append': '1',
            'pop': '1',
            'index': 'n',
            'count': 'n',
            'heappush': 'log(n)',
            'heappop': 'log(n)',
            'heapreplace': 'log(n)',
            'heappushpop': 'log(n)',
        }
        return complexities.get(func_name, '1')

    def _collect_context(self, tree: ast.AST) -> None:
        """Collect structural hints to improve classification for graph/heap search."""
        has_heap_import = False
        has_heap_calls = False
        has_while = False
        has_for = False
        has_neighbor_iter = False

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                if any(alias.name == 'heapq' for alias in node.names):
                    has_heap_import = True
            elif isinstance(node, ast.ImportFrom):
                if node.module == 'heapq':
                    has_heap_import = True

            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr in {'heappush', 'heappop', 'heapreplace', 'heappushpop'}:
                    has_heap_calls = True
                if isinstance(node.func, ast.Name) and node.func.id in {'heappush', 'heappop', 'heapreplace', 'heappushpop'}:
                    has_heap_calls = True

            if isinstance(node, ast.While):
                has_while = True
            if isinstance(node, ast.For):
                has_for = True
                if isinstance(node.iter, ast.Name) and node.iter.id in {'neighbors', 'adj', 'adjacency', 'edges'}:
                    has_neighbor_iter = True

        self.has_heap_usage = has_heap_import or has_heap_calls
        self.has_graph_search_pattern = has_while and has_for and (has_neighbor_iter or has_heap_calls)
    
    def _complexity_to_enum(self, complexity: str) -> TimeComplexity:
        """Convert string complexity to enum"""
        mapping = {
            '1': TimeComplexity.CONSTANT,
            'log(n)': TimeComplexity.LOGARITHMIC,
            'n': TimeComplexity.LINEAR,
            'n*log(n)': TimeComplexity.LINEARITHMIC,
            'n^2': TimeComplexity.QUADRATIC,
            'n^3': TimeComplexity.CUBIC,
            '2^n': TimeComplexity.EXPONENTIAL,
            'n!': TimeComplexity.FACTORIAL
        }
        return mapping.get(complexity, TimeComplexity.UNKNOWN)