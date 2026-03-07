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

    # Mapping from pattern name to quantum algorithm details
    QUANTUM_MAPPINGS = {
        'factoring': {
            'quantum_algo': "Shor's Algorithm",
            'speedup': 'Exponential vs sub-exponential',
            'suitability_score': 0.95
        },
        'fourier_transform': {
            'quantum_algo': 'Quantum Fourier Transform (QFT)',
            'speedup': 'O(log² N) vs O(N log N)',
            'suitability_score': 0.9
        },
        'period_finding': {
            'quantum_algo': "Simon's Algorithm",
            'speedup': 'Exponential vs classical exponential',
            'suitability_score': 0.85
        },
        'linear_system': {
            'quantum_algo': 'HHL Algorithm',
            'speedup': 'Exponential for certain matrices',
            'suitability_score': 0.8
        },
        'linear_search': {
            'quantum_algo': 'Grover Search',
            'speedup': 'O(√n) vs O(n)',
            'suitability_score': 0.9
        },
        'coin_flip': {
            'quantum_algo': 'Hadamard Randomness',
            'speedup': 'True randomness vs pseudo-random',
            'suitability_score': 0.7
        },
        'parity_check': {
            'quantum_algo': "Deutsch's Algorithm",
            'speedup': '1 query vs 2 queries',
            'suitability_score': 0.75
        },
        'hidden_bitstring': {
            'quantum_algo': 'Bernstein–Vazirani Algorithm',
            'speedup': '1 query vs n queries',
            'suitability_score': 0.85
        },
        'swap': {
            'quantum_algo': 'Quantum SWAP (3 CNOTs)',
            'speedup': 'No classical analogue (quantum operation)',
            'suitability_score': 0.6
        },
        'state_copy': {
            'quantum_algo': 'Quantum Teleportation',
            'speedup': 'Transmits quantum state using entanglement',
            'suitability_score': 0.7
        }
    }

    def __init__(self):
        self.patterns = self._initialize_patterns()

    def _initialize_patterns(self):
        """List of pattern detectors with names."""
        return [
            {'name': 'factoring', 'detector': self._detect_factoring},
            {'name': 'fourier_transform', 'detector': self._detect_fourier},
            {'name': 'period_finding', 'detector': self._detect_period_finding},
            {'name': 'linear_system', 'detector': self._detect_linear_system},
            {'name': 'linear_search', 'detector': self._detect_linear_search},
            {'name': 'coin_flip', 'detector': self._detect_coin_flip},
            {'name': 'parity_check', 'detector': self._detect_parity_check},
            {'name': 'hidden_bitstring', 'detector': self._detect_hidden_bitstring},
            {'name': 'swap', 'detector': self._detect_swap},
            {'name': 'state_copy', 'detector': self._detect_state_copy},
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
            'condition_count': 0,
            'has_import': False
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
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                metrics['has_import'] = True

        return metrics

    # ==================== PATTERN DETECTORS ====================

    def _detect_factoring(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Detect trial division factoring:
        - Loop from 2 to sqrt(n)
        - Modulo check
        - Return factors when found
        """
        detected = False
        confidence = 0.0

        for node in ast.walk(tree):
            # Look for a for or while loop
            if isinstance(node, (ast.For, ast.While)):
                # Check if loop has a modulo operation and a return
                has_mod = False
                has_return = False
                for sub in ast.walk(node):
                    if isinstance(sub, ast.BinOp) and isinstance(sub.op, ast.Mod):
                        has_mod = True
                    if isinstance(sub, ast.Return):
                        has_return = True
                if has_mod and has_return:
                    # Also check for range starting at 2 (common in factoring)
                    if isinstance(node, ast.For):
                        if isinstance(node.iter, ast.Call):
                            if isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range':
                                args = node.iter.args
                                if len(args) >= 2:
                                    if isinstance(args[0], ast.Constant) and args[0].value == 2:
                                        detected = True
                                        confidence = 0.9
                                        break
                    # Could also be a while loop with variable starting at 2
                    if isinstance(node, ast.While):
                        # crude check: look for assignment of a variable to 2 before loop
                        # but for simplicity, if we have mod and return, consider it factoring
                        detected = True
                        confidence = 0.7
                        break

        return {'detected': detected, 'confidence': confidence}

    def _detect_fourier(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Detect DFT implementation:
        - Nested loops over range(N)
        - Use of complex exponentials (cmath.exp, math.exp with -2j*pi*k*n/N)
        - Summation accumulator
        """
        detected = False
        confidence = 0.0

        has_nested_loops = False
        has_complex_exp = False
        has_sum = False

        for node in ast.walk(tree):
            # Look for nested loops
            if isinstance(node, (ast.For, ast.While)):
                for inner in ast.walk(node):
                    if isinstance(inner, (ast.For, ast.While)) and inner != node:
                        has_nested_loops = True
                        break

            # Look for complex exponential calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'exp' and isinstance(node.func.value, ast.Name):
                        if node.func.value.id in ('cmath', 'math'):
                            # Check if arguments involve -2j*pi etc.
                            has_complex_exp = True
                elif isinstance(node.func, ast.Name) and node.func.id == 'exp':
                    # Could be from math or cmath after import
                    has_complex_exp = True

            # Look for accumulator pattern
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in ('total', 'sum', 'X', 'A'):
                        if isinstance(node.value, ast.Constant) and node.value.value == 0:
                            # Possible initialisation
                            pass
            if isinstance(node, ast.AugAssign):
                if isinstance(node.op, ast.Add):
                    has_sum = True

        if has_nested_loops and has_complex_exp:
            confidence = 0.9
            detected = True
        elif has_nested_loops and has_sum:
            confidence = 0.6
            detected = True

        return {'detected': detected, 'confidence': confidence}

    def _detect_period_finding(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Detect brute-force period finding:
        - Loop over candidate period r
        - Check f(x) == f(x+r) for all x
        - Often uses all() or a nested loop
        """
        detected = False
        confidence = 0.0

        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Look for a loop that iterates over range(1, something)
                if isinstance(node.iter, ast.Call):
                    if isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range':
                        args = node.iter.args
                        if len(args) >= 1 and isinstance(args[0], ast.Constant) and args[0].value == 1:
                            # Inside, check for a condition comparing function calls
                            for sub in ast.walk(node):
                                if isinstance(sub, ast.If):
                                    # Look for comparisons like f(x) == f(x + r)
                                    for test_node in ast.walk(sub.test):
                                        if isinstance(test_node, ast.Compare):
                                            left = test_node.left
                                            comparators = test_node.comparators
                                            if (isinstance(left, ast.Call) and
                                                len(comparators) == 1 and
                                                isinstance(comparators[0], ast.Call)):
                                                # Could be f(x) == f(x+r)
                                                detected = True
                                                confidence = 0.8
                                                break
                                if detected:
                                    break
                        if detected:
                            break

        return {'detected': detected, 'confidence': confidence}

    def _detect_linear_system(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Detect Gaussian elimination / linear system solver:
        - Nested loops over rows/columns
        - Operations like A[j][k] -= factor * A[i][k]
        - Back substitution loop
        """
        detected = False
        confidence = 0.0

        has_nested_loops = False
        has_row_ops = False
        has_backsub = False

        for node in ast.walk(tree):
            # Nested loops
            if isinstance(node, (ast.For, ast.While)):
                for inner in ast.walk(node):
                    if isinstance(inner, (ast.For, ast.While)) and inner != node:
                        has_nested_loops = True
                        break

            # Look for AugAssign with multiplication/division (factor operations)
            if isinstance(node, ast.AugAssign):
                if isinstance(node.op, (ast.Sub, ast.Add)) and isinstance(node.value, ast.BinOp):
                    if isinstance(node.value.op, (ast.Mult, ast.Div)):
                        has_row_ops = True

            # Back substitution: loop from n-1 down to 0
            if isinstance(node, ast.For):
                if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name):
                    if node.iter.func.id == 'range':
                        args = node.iter.args
                        if len(args) == 3:
                            # range(n-1, -1, -1)
                            if (isinstance(args[0], ast.BinOp) and
                                isinstance(args[1], ast.UnaryOp) and
                                isinstance(args[2], ast.UnaryOp)):
                                has_backsub = True

        if has_nested_loops and has_row_ops:
            confidence = 0.85
            detected = True
        elif has_backsub:
            confidence = 0.7
            detected = True

        return {'detected': detected, 'confidence': confidence}

    def _detect_linear_search(self, tree: ast.AST) -> Dict[str, Any]:
        """Detect linear search pattern (loop with comparison and return)."""
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

    def _detect_coin_flip(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Detect coin flip / random bit generation:
        - Import random
        - Function returning random.choice([0,1]), random.randint(0,1), or random.random() < 0.5
        """
        detected = False
        confidence = 0.0

        has_random_import = False
        has_coin_return = False

        for node in ast.walk(tree):
            # Check for random import
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    if alias.name == 'random' or (isinstance(node, ast.ImportFrom) and node.module == 'random'):
                        has_random_import = True
                        break

            # Look for return statements with random calls
            if isinstance(node, ast.Return):
                if isinstance(node.value, ast.Call):
                    func = node.value.func
                    # random.choice([0,1])
                    if (isinstance(func, ast.Attribute) and func.attr == 'choice' and
                        isinstance(func.value, ast.Name) and func.value.id == 'random'):
                        if len(node.value.args) == 1:
                            arg = node.value.args[0]
                            if isinstance(arg, ast.List) and len(arg.elts) == 2:
                                if all(isinstance(elt, ast.Constant) and elt.value in (0,1) for elt in arg.elts):
                                    has_coin_return = True
                    # random.randint(0,1)
                    elif (isinstance(func, ast.Attribute) and func.attr == 'randint' and
                          isinstance(func.value, ast.Name) and func.value.id == 'random'):
                        if len(node.value.args) == 2:
                            if (isinstance(node.value.args[0], ast.Constant) and node.value.args[0].value == 0 and
                                isinstance(node.value.args[1], ast.Constant) and node.value.args[1].value == 1):
                                has_coin_return = True
                    # random.random() < 0.5 (inside a comparison)
                elif isinstance(node.value, ast.Compare):
                    left = node.value.left
                    if (isinstance(left, ast.Call) and isinstance(left.func, ast.Attribute) and
                        left.func.attr == 'random' and isinstance(left.func.value, ast.Name) and
                        left.func.value.id == 'random'):
                        if len(node.value.ops) == 1 and isinstance(node.value.ops[0], ast.Lt):
                            right = node.value.comparators[0]
                            if isinstance(right, ast.Constant) and right.value == 0.5:
                                has_coin_return = True

        if has_random_import and has_coin_return:
            detected = True
            confidence = 0.95
        elif has_coin_return:
            detected = True
            confidence = 0.7

        return {'detected': detected, 'confidence': confidence}

    def _detect_parity_check(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Detect function that checks if f(0) == f(1):
        - Function takes a callable parameter
        - Body compares calls with arguments 0 and 1
        """
        detected = False
        confidence = 0.0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function has at least one parameter
                if len(node.args.args) >= 1:
                    # Look for a return statement that compares two calls
                    for sub in ast.walk(node):
                        if isinstance(sub, ast.Return):
                            if isinstance(sub.value, ast.Compare):
                                left = sub.value.left
                                right = sub.value.comparators
                                if len(right) == 1:
                                    # Both sides should be calls
                                    if isinstance(left, ast.Call) and isinstance(right[0], ast.Call):
                                        # Check arguments: left call has arg 0, right call has arg 1 (or vice versa)
                                        left_args = left.args
                                        right_args = right[0].args
                                        if (len(left_args) == 1 and len(right_args) == 1 and
                                            isinstance(left_args[0], ast.Constant) and
                                            isinstance(right_args[0], ast.Constant)):
                                            vals = {left_args[0].value, right_args[0].value}
                                            if vals == {0, 1}:
                                                detected = True
                                                confidence = 0.9
                                                break
                        if detected:
                            break
                if detected:
                    break

        return {'detected': detected, 'confidence': confidence}

    def _detect_hidden_bitstring(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Detect Bernstein–Vazirani style:
        - Loop over range(n)
        - Inside, construct a probe (list with 1 at position i or bit shift)
        - Call oracle with probe, collect results
        """
        detected = False
        confidence = 0.0

        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Loop over range(n)
                if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name):
                    if node.iter.func.id == 'range':
                        # Check body for probe construction and oracle call
                        has_probe = False
                        has_oracle_call = False
                        for sub in ast.walk(node):
                            # Probe construction: list with 1 at position i, or 1 << i
                            if isinstance(sub, ast.Assign):
                                if isinstance(sub.value, ast.List):
                                    # Could be a list with zeros and a 1
                                    for idx, elt in enumerate(sub.value.elts):
                                        if isinstance(elt, ast.Constant) and elt.value == 1:
                                            # Check if other elements are 0
                                            other_zeros = all(isinstance(e, ast.Constant) and e.value == 0
                                                              for j, e in enumerate(sub.value.elts) if j != idx)
                                            if other_zeros:
                                                has_probe = True
                                                break
                            if isinstance(sub, ast.Call):
                                # Oracle call with probe
                                if len(sub.args) >= 1:
                                    arg = sub.args[0]
                                    if isinstance(arg, ast.Name) and arg.id in ('probe', 'bits'):  # variable name
                                        has_oracle_call = True
                                    elif isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.LShift):
                                        # 1 << i
                                        has_oracle_call = True
                        if has_probe and has_oracle_call:
                            detected = True
                            confidence = 0.85
                            break
                if detected:
                    break

        return {'detected': detected, 'confidence': confidence}

    def _detect_swap(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Detect variable swap:
        - Tuple assignment a, b = b, a
        - Or three-assignment with temp variable
        """
        detected = False
        confidence = 0.0

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Tuple swap: a, b = b, a
                if (isinstance(node.targets[0], ast.Tuple) and
                    isinstance(node.value, ast.Tuple) and
                    len(node.targets[0].elts) == 2 and
                    len(node.value.elts) == 2):
                    # Check that the tuple elements are swapped
                    left_names = [elt.id for elt in node.targets[0].elts if isinstance(elt, ast.Name)]
                    right_names = [elt.id for elt in node.value.elts if isinstance(elt, ast.Name)]
                    if len(left_names) == 2 and len(right_names) == 2:
                        if left_names[0] == right_names[1] and left_names[1] == right_names[0]:
                            detected = True
                            confidence = 0.95
                            break

                # Three-assignment swap: temp = a; a = b; b = temp
                # We need to find a block of three assignments with a temp variable
                # This is harder; we'll look for a pattern of two assignments using a common temporary
                # For simplicity, we'll check if there are two assignments with the same variable on LHS and RHS
                # Not implemented fully due to complexity; we'll rely on tuple swap detection mostly.

        return {'detected': detected, 'confidence': confidence}

    def _detect_state_copy(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Detect state copying / sending:
        - Function that assigns one parameter to another
        - Or calls a method like write/send on a parameter with another parameter as argument
        """
        detected = False
        confidence = 0.0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Look for assignments where RHS is a parameter and LHS is another parameter or variable
                params = {arg.arg for arg in node.args.args}
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Assign):
                        for target in sub.targets:
                            if isinstance(target, ast.Name):
                                if target.id in params and isinstance(sub.value, ast.Name):
                                    if sub.value.id in params and sub.value.id != target.id:
                                        # Assignment from one parameter to another
                                        detected = True
                                        confidence = 0.8
                                        break
                    if isinstance(sub, ast.Call):
                        # Method call like channel.write(state)
                        if isinstance(sub.func, ast.Attribute):
                            if sub.func.attr in ('write', 'send', 'receive'):
                                if sub.args and isinstance(sub.args[0], ast.Name):
                                    if sub.args[0].id in params:
                                        detected = True
                                        confidence = 0.9
                                        break
                    if detected:
                        break
                if detected:
                    break

        return {'detected': detected, 'confidence': confidence}

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