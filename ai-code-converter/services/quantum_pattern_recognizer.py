"""
AST-based Quantum Pattern Recognizer Service
"""
import ast
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class SuitabilityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class PatternInfo:
    name: str
    confidence: float
    quantum_algo: str
    speedup: str
    suitability_score: float


@dataclass
class AnalysisResult:
    success: bool
    patterns: List[PatternInfo]
    suitability_score: float
    suitability_level: SuitabilityLevel
    message: str
    metrics: Dict[str, Any]
    error: str = None


class QuantumPatternRecognizer:
    """AST-based pattern recognizer for quantum-amenable algorithms."""
    
    QUANTUM_MAPPINGS = {
        'linear_search': {
            'quantum_algo': 'Grover Search',
            'speedup': 'O(√n) vs O(n)',
            'suitability_score': 0.9
        },
        'binary_search': {
            'quantum_algo': 'Quantum Binary Search',
            'speedup': 'O(log n) with better constants',
            'suitability_score': 0.7
        },
        'brute_force_optimization': {
            'quantum_algo': 'QAOA (Quantum Approximate Optimization Algorithm)',
            'speedup': 'Quadratic speedup for combinatorial problems',
            'suitability_score': 0.85
        },
        'min_max_problem': {
            'quantum_algo': 'Quantum Minimum Finding (Dürr-Høyer)',
            'speedup': 'O(√n) vs O(n)',
            'suitability_score': 0.8
        },
        'sorting_algorithm': {
            'quantum_algo': 'Quantum Comparison-Based Sort',
            'speedup': 'Better comparison operations',
            'suitability_score': 0.6
        }
    }
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self):
        return [
            {'name': 'linear_search', 'detector': self._detect_linear_search},
            {'name': 'binary_search', 'detector': self._detect_binary_search},
            {'name': 'brute_force_optimization', 'detector': self._detect_brute_force_opt},
            {'name': 'min_max_problem', 'detector': self._detect_min_max_problem},
            {'name': 'sorting_algorithm', 'detector': self._detect_sorting_algorithm}
        ]
    
    def analyze(self, python_code: str) -> AnalysisResult:
        """Main analysis function."""
        try:
            tree = ast.parse(python_code)
            metrics = self._extract_metrics(tree, python_code)
            
            # Detect patterns
            detected_patterns = []
            for pattern in self.patterns:
                result = pattern['detector'](tree)
                if result['detected']:
                    quantum_info = self.QUANTUM_MAPPINGS.get(pattern['name'], {})
                    pattern_info = PatternInfo(
                        name=pattern['name'],
                        confidence=result['confidence'],
                        quantum_algo=quantum_info.get('quantum_algo', 'Unknown'),
                        speedup=quantum_info.get('speedup', 'Unknown'),
                        suitability_score=quantum_info.get('suitability_score', 0.5)
                    )
                    detected_patterns.append(pattern_info)
            
            # Calculate suitability
            suitability = self._calculate_suitability(detected_patterns)
            
            return AnalysisResult(
                success=True,
                patterns=detected_patterns,
                suitability_score=suitability['score'],
                suitability_level=SuitabilityLevel(suitability['level']),
                message=suitability['message'],
                metrics=metrics
            )
            
        except SyntaxError as e:
            return AnalysisResult(
                success=False,
                patterns=[],
                suitability_score=0.0,
                suitability_level=SuitabilityLevel.LOW,
                message=f'Syntax error: {str(e)}',
                metrics={},
                error=f'Syntax error: {str(e)}'
            )
        except Exception as e:
            return AnalysisResult(
                success=False,
                patterns=[],
                suitability_score=0.0,
                suitability_level=SuitabilityLevel.LOW,
                message=f'Analysis error: {str(e)}',
                metrics={},
                error=f'Analysis error: {str(e)}'
            )
    
    def _extract_metrics(self, tree: ast.AST, python_code: str) -> Dict[str, Any]:
        """Extract basic code metrics."""
        metrics = {
            'has_function': False,
            'has_loop': False,
            'has_condition': False,
            'line_count': len(python_code.split('\n')) if python_code else 0,
            'function_count': 0,
            'loop_count': 0,
            'condition_count': 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                metrics['has_function'] = True
                metrics['function_count'] += 1
            if isinstance(node, (ast.For, ast.While)):
                metrics['has_loop'] = True
                metrics['loop_count'] += 1
            if isinstance(node, ast.If):
                metrics['has_condition'] = True
                metrics['condition_count'] += 1
        
        return metrics
    
    # ===== PATTERN DETECTORS =====
    
    def _detect_linear_search(self, tree: ast.AST) -> Dict[str, Any]:
        """Detect linear search pattern."""
        detected = False
        confidence = 0.0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                has_compare = False
                has_exit = False
                
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Compare):
                        has_compare = True
                    if isinstance(stmt, (ast.Return, ast.Break)):
                        has_exit = True
                
                if has_compare and has_exit:
                    detected = True
                    confidence = 0.9
                    break
        
        return {'detected': detected, 'confidence': confidence}
    
    def _detect_binary_search(self, tree: ast.AST) -> Dict[str, Any]:
        """Detect binary search."""
        detected = False
        confidence = 0.0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.While):
                # Simple check for binary search structure
                if self._has_mid_calculation(node.body):
                    detected = True
                    confidence = 0.8
                    break
        
        return {'detected': detected, 'confidence': confidence}
    
    def _detect_brute_force_opt(self, tree: ast.AST) -> Dict[str, Any]:
        """Detect brute force optimization."""
        detected = False
        confidence = 0.0
        
        # Count nested loops
        max_nesting = 0
        current_nesting = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            elif isinstance(node, ast.FunctionDef):
                current_nesting = 0
        
        if max_nesting >= 2:
            detected = True
            confidence = min(0.7 + (max_nesting * 0.1), 0.95)
        
        return {'detected': detected, 'confidence': confidence}
    
    def _detect_min_max_problem(self, tree: ast.AST) -> Dict[str, Any]:
        """Detect min/max finding."""
        detected = False
        confidence = 0.0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_minmax_var = False
                has_comparison = False
                
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Assign):
                        if len(stmt.targets) == 1:
                            if isinstance(stmt.targets[0], ast.Name):
                                var_name = stmt.targets[0].id.lower()
                                if var_name.startswith(('min', 'max')):
                                    has_minmax_var = True
                    
                    if isinstance(stmt, ast.Compare):
                        has_comparison = True
                
                if has_minmax_var and has_comparison:
                    detected = True
                    confidence = 0.85
                    break
        
        return {'detected': detected, 'confidence': confidence}
    
    def _detect_sorting_algorithm(self, tree: ast.AST) -> Dict[str, Any]:
        """Detect sorting algorithm."""
        detected = False
        confidence = 0.0
        
        has_nested_loops = False
        has_swap = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                for inner in ast.walk(node):
                    if isinstance(inner, ast.For):
                        has_nested_loops = True
                    if isinstance(inner, ast.Assign):
                        if isinstance(inner.value, ast.Tuple):
                            has_swap = True
        
        if has_nested_loops and has_swap:
            detected = True
            confidence = 0.8
        
        return {'detected': detected, 'confidence': confidence}
    
    def _has_mid_calculation(self, body: List[ast.AST]) -> bool:
        """Check for mid calculation."""
        for node in ast.walk(ast.Module(body=body)):
            if isinstance(node, ast.Assign):
                if isinstance(node.value, ast.BinOp):
                    if isinstance(node.value.op, ast.FloorDiv):
                        return True
        return False
    
    def _calculate_suitability(self, patterns: List[PatternInfo]) -> Dict[str, Any]:
        """Calculate quantum suitability."""
        if not patterns:
            return {
                'score': 0.0,
                'level': 'low',
                'message': 'No quantum-amenable patterns detected'
            }
        
        # Calculate weighted score
        total_score = 0.0
        for pattern in patterns:
            base_score = pattern.suitability_score
            confidence = pattern.confidence
            total_score += base_score * confidence
        
        avg_score = total_score / len(patterns)
        
        if avg_score >= 0.7:
            level = 'high'
            message = 'Strong candidate for quantum conversion'
        elif avg_score >= 0.4:
            level = 'medium'
            message = 'Moderate quantum advantage potential'
        else:
            level = 'low'
            message = 'Limited quantum advantage expected'
        
        return {
            'score': round(avg_score, 3),
            'level': level,
            'message': message
        }


# Create singleton instance
recognizer = QuantumPatternRecognizer()