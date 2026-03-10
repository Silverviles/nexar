"""
Classical Complexity Analyzer
Calculates cyclomatic complexity, time complexity, space complexity
"""
import ast
import logging
import re
from typing import Dict, Any, Tuple
from radon.complexity import cc_visit
from models.analysis_result import ClassicalComplexity, TimeComplexity
from models.unified_ast import UnifiedAST
from modules.accurate_time_complexity import AccurateTimeComplexityAnalyzer
from modules.space_complexity_analyzer import AccurateSpaceComplexityAnalyzer

logger = logging.getLogger(__name__)

class ComplexityAnalyzer:
    """Analyzes classical code complexity"""
    
    def __init__(self):
        self.time_analyzer = AccurateTimeComplexityAnalyzer()
        self.space_analyzer = AccurateSpaceComplexityAnalyzer()
    
    def analyze(
        self,
        code: str,
        metadata: Dict[str, Any],
        unified_ast: UnifiedAST = None,
    ) -> ClassicalComplexity:
        """
        Analyze classical complexity metrics
        
        Args:
            code: Source code string
            metadata: Metadata from parser
            
        Returns:
            ClassicalComplexity object
        """
        if unified_ast and unified_ast.canonical_ir:
            ir_meta = unified_ast.canonical_ir.metadata or {}
            metadata = {
                **metadata,
                'loop_count': unified_ast.canonical_ir.loop_count,
                'conditional_count': unified_ast.canonical_ir.conditional_count,
                'nesting_depth': unified_ast.canonical_ir.max_nesting_depth,
                'control_flow_nesting_depth': ir_meta.get('control_flow_nesting_depth', unified_ast.canonical_ir.max_nesting_depth),
                'structural_nesting_depth': ir_meta.get('structural_nesting_depth', unified_ast.canonical_ir.max_nesting_depth),
                'lines_of_code': ir_meta.get('lines_of_code', metadata.get('lines_of_code', 0)),
            }

        cyclomatic, cyclomatic_max = self.calculate_cyclomatic_complexity(code)
        cognitive = self.calculate_cognitive_complexity(code)
        time_complexity = self.time_analyzer.analyze(code)
        space_complexity = self.space_analyzer.analyze(code)
        
        logger.info(
            "Classical complexity: cyclomatic=%d, cognitive=%d, time=%s, space=%s",
            cyclomatic, cognitive, time_complexity.value if hasattr(time_complexity, 'value') else time_complexity, space_complexity,
        )
        
        return ClassicalComplexity(
            cyclomatic_complexity=cyclomatic,
            cyclomatic_complexity_max=cyclomatic_max,
            cognitive_complexity=cognitive,
            time_complexity=time_complexity,
            space_complexity=space_complexity,
            loop_count=metadata.get('loop_count', 0),
            conditional_count=metadata.get('conditional_count', 0),
            function_count=metadata.get('function_count', 0),
            max_nesting_depth=metadata.get('control_flow_nesting_depth', metadata.get('nesting_depth', 0)),
            control_flow_nesting_depth=metadata.get('control_flow_nesting_depth', metadata.get('nesting_depth', 0)),
            structural_nesting_depth=metadata.get('structural_nesting_depth', metadata.get('nesting_depth', 0)),
            lines_of_code=metadata.get('lines_of_code', 0)
        )
    
    def calculate_cyclomatic_complexity(self, code: str) -> Tuple[int, int]:
        """
        Calculate McCabe cyclomatic complexity
        Uses radon library for Python code
        """
        try:
            complexity_results = cc_visit(code)
            if complexity_results:
                total = sum(item.complexity for item in complexity_results)
                max_complexity = max(item.complexity for item in complexity_results)
                return total, max_complexity
            return 1, 1  # Base complexity
        except Exception:
            logger.warning("cc_visit failed for cyclomatic complexity, using manual fallback", exc_info=True)
            fallback = self._calculate_complexity_manual(code)
            return fallback, fallback
        
    def calculate_cognitive_complexity(self, code: str) -> int:
        """AST-based cognitive complexity (nesting-aware)."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            logger.warning("SyntaxError during cognitive complexity analysis, defaulting to 1")
            return 1

        def score_block(statements, nesting: int) -> int:
            total_score = 0
            for stmt in statements:
                if isinstance(stmt, (ast.If, ast.For, ast.While, ast.AsyncFor)):
                    total_score += 1 + nesting
                    total_score += score_block(getattr(stmt, 'body', []), nesting + 1)
                    total_score += score_block(getattr(stmt, 'orelse', []), nesting)
                elif isinstance(stmt, ast.Try):
                    total_score += 1 + nesting
                    total_score += score_block(stmt.body, nesting + 1)
                    for handler in stmt.handlers:
                        total_score += 1 + nesting
                        total_score += score_block(handler.body, nesting + 1)
                    total_score += score_block(stmt.orelse, nesting)
                    total_score += score_block(stmt.finalbody, nesting)
                elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    total_score += score_block(stmt.body, nesting)
                else:
                    if isinstance(stmt, (ast.Break, ast.Continue)):
                        total_score += 1
            return total_score

        total = score_block(getattr(tree, 'body', []), 0)
        return max(total, 1)
    
    def _calculate_complexity_manual(self, code: str) -> int:
        """
        Manual cyclomatic complexity calculation
        Formula: M = E - N + 2P
        Simplified: count decision points + 1
        """
        decision_keywords = ['if', 'elif', 'else', 'for', 'while', 
                           'try', 'except', 'and', 'or', '?']
        
        complexity = 1  # Base complexity
        for line in code.split('\n'):
            line_lower = line.lower()
            for keyword in decision_keywords:
                complexity += line_lower.count(keyword)
        
        return min(complexity, 50)  # Cap at 50
    
    def estimate_time_complexity(self, code: str, metadata: Dict[str, Any]) -> TimeComplexity:
        """
        Estimate time complexity based on code structure
        Simple heuristic-based approach
        """
        loop_count = metadata.get('loop_count', 0)
        nesting_depth = metadata.get('nesting_depth', 0)
        
        # Check for specific patterns
        has_factorial = 'factorial' in code.lower() or '!' in code
        has_exponential = any(term in code.lower() for term in ['pow', '**', '^'])
        has_recursion = self._has_recursion(code)
        
        # Heuristic rules
        if has_factorial:
            return TimeComplexity.FACTORIAL
        
        if has_exponential and has_recursion:
            return TimeComplexity.EXPONENTIAL
        
        if nesting_depth >= 3 or loop_count >= 3:
            return TimeComplexity.CUBIC
        
        if nesting_depth >= 2 or loop_count >= 2:
            return TimeComplexity.QUADRATIC
        
        if loop_count == 1:
            # Check for sorting or binary search patterns
            if any(term in code.lower() for term in ['sort', 'sorted', 'quicksort', 'mergesort']):
                return TimeComplexity.LINEARITHMIC
            return TimeComplexity.LINEAR
        
        if loop_count == 0:
            if 'log' in code.lower() or 'binary' in code.lower():
                return TimeComplexity.LOGARITHMIC
            return TimeComplexity.CONSTANT
        
        return TimeComplexity.UNKNOWN
    
    def estimate_space_complexity(self, code: str) -> str:
        """
        Estimate space complexity
        Simple pattern-based estimation
        """
        # Check for data structure allocations
        has_list = any(term in code for term in ['[]', 'list(', 'List['])
        has_dict = any(term in code for term in ['{}', 'dict(', 'Dict['])
        has_set = 'set(' in code
        
        # Check for recursive calls (stack space)
        has_recursion = self._has_recursion(code)
        
        # Count nested structures
        nesting_level = code.count('[') + code.count('{')
        
        if has_recursion:
            return "O(n)"  # Stack space
        
        if nesting_level > 3 or (has_list and has_dict):
            return "O(n^2)"
        
        if has_list or has_dict or has_set:
            return "O(n)"
        
        return "O(1)"
    
    def _has_recursion(self, code: str) -> bool:
        """Detect recursive function calls"""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    # Check if function calls itself
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Name) and child.func.id == func_name:
                                return True
        except Exception:
            logger.debug("AST parsing failed for recursion detection, falling back to regex", exc_info=True)
            # Fallback regex
            pattern = r'def\s+(\w+)\s*\([^)]*\):.*\1\s*\('
            return bool(re.search(pattern, code, re.DOTALL))
        
        return False