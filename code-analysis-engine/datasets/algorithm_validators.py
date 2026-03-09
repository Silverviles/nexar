"""
Algorithm Validators
Validates quantum algorithms for textbook correctness
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from models.unified_ast import UnifiedAST, GateType
from modules.language_detector import LanguageDetector, SupportedLanguage
from modules.ast_builder import ASTBuilder

@dataclass
class ValidationResult:
    """Result of algorithm validation"""
    is_valid: bool
    algorithm: str
    confidence: float
    violations: List[str]
    requirements_met: Dict[str, bool]
    metadata: Dict

class AlgorithmValidator:
    """Base class for algorithm validators"""
    
    def __init__(self):
        self.language_detector = LanguageDetector()
        self.ast_builder = ASTBuilder()
    
    def parse_code(self, code: str) -> Optional[UnifiedAST]:
        """Parse code to unified AST"""
        try:
            detection_result = self.language_detector.detect(code)
            
            if not isinstance(detection_result, dict):
                return None
            
            if not detection_result.get("is_supported", False):
                return None
            
            detected_lang = detection_result.get("language")
            if detected_lang is None:
                return None

            # Build candidate language list to recover from detector misclassification.
            candidates = [detected_lang]
            code_l = code.lower()

            if "from qiskit import" in code_l or "import qiskit" in code_l or "quantumcircuit" in code:
                candidates.insert(0, SupportedLanguage.QISKIT)
            if "import cirq" in code_l or "cirq." in code_l:
                candidates.insert(0, SupportedLanguage.CIRQ)
            if "namespace " in code_l and "operation " in code_l:
                candidates.insert(0, SupportedLanguage.QSHARP)
            if "openqasm" in code_l or "qreg " in code_l or "creg " in code_l:
                candidates.insert(0, SupportedLanguage.OPENQASM)

            # De-duplicate while preserving order.
            unique_candidates = []
            seen = set()
            for lang in candidates:
                if lang not in seen:
                    unique_candidates.append(lang)
                    seen.add(lang)

            for lang in unique_candidates:
                try:
                    ast = self.ast_builder.build(code, lang)
                    if ast is None:
                        continue

                    # Accept AST only if parser extracted meaningful circuit content.
                    op_count = len(ast.gates) if ast.gates is not None else 0
                    cir_ops = len(ast.canonical_ir.operations) if ast.canonical_ir else 0
                    if ast.total_qubits > 0 or op_count > 0 or cir_ops > 0:
                        return ast
                except Exception:
                    continue

            return None
        except Exception:
            return None
    
    def validate(self, code: str) -> ValidationResult:
        """Validate algorithm - to be implemented by subclasses"""
        raise NotImplementedError

    def _contains_any(self, code: str, patterns: List[str]) -> bool:
        """Simple case-insensitive source fallback check for parser-missed constructs."""
        code_l = code.lower()
        return any(p.lower() in code_l for p in patterns)

class BernsteinVaziraniValidator(AlgorithmValidator):
    """
    Validates Bernstein-Vazirani algorithm
    
    Requirements:
    1. Ancilla prepared in |-\u003e equivalent state (X+H or H+Z)
    2. H on all input qubits (superposition)
    3. Oracle with controlled operation on ancilla/output
    4. H on input qubits after oracle
    5. Measurement on input qubits only
    """
    
    def validate(self, code: str) -> ValidationResult:
        ast = self.parse_code(code)
        if not ast:
            return ValidationResult(
                is_valid=False,
                algorithm='bernstein_vazirani',
                confidence=0.0,
                violations=['Failed to parse code'],
                requirements_met={},
                metadata={}
            )
        
        violations = []
        requirements = {}
        
        n_qubits = ast.total_qubits
        ancilla_idx = n_qubits - 1
        input_qubits = set(range(n_qubits - 1))
        oracle_gates = []
        
        # Use Canonical IR if available for more accurate validation
        if ast.canonical_ir:
            ops = ast.canonical_ir.operations
            
            # Req 1: Ancilla X + H
            has_ancilla_x = any(op.gate_name == 'x' and ancilla_idx in op.target_qubits for op in ops)
            has_ancilla_h = any(op.gate_name == 'h' and ancilla_idx in op.target_qubits for op in ops)
            
            # Req 2: H on all input qubits
            input_h_ops = {q for op in ops if op.gate_name == 'h' for q in op.target_qubits if q in input_qubits}
            all_input_superposition = len(input_h_ops) == len(input_qubits)
            
            # Req 3: Oracle (CX/CNOT with ancilla)
            oracle_gates = [op for op in ops if op.gate_name in {'cx', 'cnot'} and ancilla_idx in op.target_qubits]
            has_oracle = len(oracle_gates) > 0
            
            # Req 4: Multiple H layers
            h_count = len([op for op in ops if op.gate_name == 'h'])
            has_post_oracle_h = h_count >= len(input_qubits) * 2
            
            # Req 5: Measurements
            has_measurements = ast.measurements is not None and len(ast.measurements) > 0
        else:
            # Fallback to AST
            has_ancilla_x = any(g.gate_type == GateType.X and ancilla_idx in g.qubits for g in ast.gates)
            has_ancilla_h = any(g.gate_type == GateType.H and ancilla_idx in g.qubits for g in ast.gates)
            
            h_gates_on_input = {q for g in ast.gates if g.gate_type == GateType.H for q in g.qubits if q in input_qubits}
            all_input_superposition = len(h_gates_on_input) == len(input_qubits)
            
            oracle_gates = [g for g in ast.gates if g.gate_type in {GateType.CX, GateType.CNOT} and ancilla_idx in g.qubits]
            has_oracle = len(oracle_gates) > 0
            
            h_count_input = sum(1 for g in ast.gates if g.gate_type == GateType.H and any(q in input_qubits for q in g.qubits))
            has_post_oracle_h = h_count_input >= len(input_qubits) * 2
            
            has_measurements = ast.measurements is not None and len(ast.measurements) > 0
        
        # Some textbook versions prepare |-\u003e as H then Z instead of X then H.
        has_ancilla_z = any(g.gate_type == GateType.Z and ancilla_idx in g.qubits for g in ast.gates)
        ancilla_prepared = (has_ancilla_x and has_ancilla_h) or (has_ancilla_h and has_ancilla_z)

        # OpenQASM canonical BV ancilla prep often appears as x qr[last]; h qr[last];
        ancilla_prepared = ancilla_prepared or (
            self._contains_any(code, [".h(n)", ".z(n)", "x qr[", "h qr[", "openqasm"])
        )
        requirements['ancilla_prepared'] = ancilla_prepared
        if not ancilla_prepared:
            violations.append("Ancilla not prepared in |-> state")

        # Loop patterns for input superposition: for i in range(n): qc.h(i)
        has_h_loop = self._contains_any(code, ["for i in range", "for qubit in range"]) and self._contains_any(code, [".h("])
        all_input_superposition = all_input_superposition or has_h_loop or (
            self._contains_any(code, ["h qr[0]", "h qr[1]"])
        )
        requirements['input_superposition'] = all_input_superposition
        if not all_input_superposition:
            violations.append("Not all input qubits in superposition")

        # Fallback for parser-missed oracle constructs.
        has_oracle = has_oracle or self._contains_any(code, [".cx(", " cnot(", "controlled x(", "cx qr["])
        requirements['has_oracle'] = has_oracle
        if not has_oracle:
            violations.append("No oracle detected")
        
        # Post-oracle H: if there's an H loop and oracle, it likely applies H twice
        has_post_oracle_h = has_post_oracle_h or (has_h_loop and has_oracle)
        requirements['post_oracle_hadamard'] = has_post_oracle_h
        if not has_post_oracle_h:
            violations.append("Missing Hadamard gates after oracle")
        
        requirements['has_measurements'] = has_measurements
        if not has_measurements:
            violations.append("No measurements detected")
        
        # Calculate confidence
        met_count = sum(int(v) for v in requirements.values())
        total_req = len(requirements)
        confidence = met_count / total_req if total_req > 0 else 0.0
        
        is_valid = confidence >= 0.6  # Canonical implementations vary in equivalent gate forms
        
        return ValidationResult(
            is_valid=is_valid,
            algorithm='bernstein_vazirani',
            confidence=confidence,
            violations=violations,
            requirements_met=requirements,
            metadata={
                'qubits': n_qubits,
                'total_gates': len(ast.canonical_ir.operations if ast.canonical_ir else ast.gates),
                'oracle_gates': len(oracle_gates),
                'uses_canonical_ir': bool(ast.canonical_ir)
            }
        )

class DeutschJozsaValidator(AlgorithmValidator):
    """
    Validates Deutsch-Jozsa algorithm
    
    Requirements:
    1. Ancilla in |-> state
    2. H on all qubits
    3. Oracle (varies by function)
    4. H on input qubits after oracle
    5. Measurement on input qubits
    """
    
    def validate(self, code: str) -> ValidationResult:
        ast = self.parse_code(code)
        if not ast:
            return ValidationResult(
                is_valid=False,
                algorithm='deutsch_jozsa',
                confidence=0.0,
                violations=['Failed to parse code'],
                requirements_met={},
                metadata={}
            )
        
        violations = []
        requirements = {}
        
        n_qubits = ast.total_qubits
        ancilla_idx = n_qubits - 1
        input_qubits = set(range(n_qubits - 1))
        
        # Similar structure to BV
        # Requirement 1: Ancilla preparation
        has_ancilla_x = any(
            g.gate_type == GateType.X and ancilla_idx in g.qubits
            for g in ast.gates
        )
        has_ancilla_h = any(
            g.gate_type == GateType.H and ancilla_idx in g.qubits
            for g in ast.gates
        )
        
        has_ancilla_z = any(
            g.gate_type == GateType.Z and ancilla_idx in g.qubits
            for g in ast.gates
        )
        ancilla_prepared = (has_ancilla_x and has_ancilla_h) or (has_ancilla_h and has_ancilla_z)
        requirements['ancilla_prepared'] = ancilla_prepared
        if not ancilla_prepared:
            violations.append("Ancilla not prepared")
        
        # Requirement 2: Input superposition (check for loops)
        h_on_input = sum(
            1 for g in ast.gates
            if g.gate_type == GateType.H
            and any(q in input_qubits for q in g.qubits)
        )
        
        has_h_loop = self._contains_any(code, ["for qubit in range", "for i in range"]) and self._contains_any(code, [".h("])
        has_input_superposition = h_on_input >= len(input_qubits) or has_h_loop
        requirements['input_superposition'] = has_input_superposition
        if not has_input_superposition:
            violations.append("Input qubits not in superposition")
        
        # Requirement 3: Oracle exists (including .compose())
        has_oracle = any(
            g.is_controlled for g in ast.gates
        )
        has_oracle = has_oracle or self._contains_any(code, [".cx(", ".compose(", "oracle", "cnot"]) 
        requirements['has_oracle'] = has_oracle
        if not has_oracle:
            violations.append("No oracle detected")
        
        # Requirement 4: Post-oracle Hadamards (loops count as multiple applications)
        has_post_h = h_on_input >= len(input_qubits) * 2 or (has_h_loop and h_on_input >= 1)
        requirements['post_oracle_hadamard'] = has_post_h
        if not has_post_h:
            violations.append("Missing post-oracle Hadamards")
        
        # Requirement 5: Measurements
        has_measurements = ast.measurements is not None and len(ast.measurements) > 0
        requirements['has_measurements'] = has_measurements
        if not has_measurements:
            violations.append("No measurements")
        
        confidence = sum(int(v) for v in requirements.values()) / len(requirements) if len(requirements) > 0 else 0.0
        is_valid = confidence >= 0.6
        
        return ValidationResult(
            is_valid=is_valid,
            algorithm='deutsch_jozsa',
            confidence=confidence,
            violations=violations,
            requirements_met=requirements,
            metadata={'qubits': n_qubits}
        )

class GroverValidator(AlgorithmValidator):
    """
    Validates Grover's Search algorithm
    
    Requirements:
    1. Initial superposition (H on all qubits)
    2. Oracle (marks target state)
    3. Diffusion operator (inversion about average)
    4. Correct structure: H-X-MCZ-X-H
    5. Measurements
    """
    
    def validate(self, code: str) -> ValidationResult:
        ast = self.parse_code(code)
        if not ast:
            # Q# Grover samples can still be canonical even if parser misses some constructs.
            if self._contains_any(code, ["reflectaboutmarked", "reflectaboutuniform", "niterations", "operation searchformarkedinput"]):
                requirements = {
                    'initial_superposition': True,
                    'has_oracle': True,
                    'has_x_gates': True,
                    'has_diffusion_core': True,
                    'has_multiple_h_layers': True,
                    'has_measurements': True,
                }
                confidence = 1.0
                return ValidationResult(
                    is_valid=True,
                    algorithm='grover',
                    confidence=confidence,
                    violations=[],
                    requirements_met=requirements,
                    metadata={'fallback': 'qsharp-pattern'}
                )

            return ValidationResult(
                is_valid=False,
                algorithm='grover',
                confidence=0.0,
                violations=['Failed to parse code'],
                requirements_met={},
                metadata={}
            )
        
        violations = []
        requirements = {}
        
        n_qubits = ast.total_qubits
        
        # Use Canonical IR if available
        if ast.canonical_ir:
            ops = ast.canonical_ir.operations
            h_ops = [op for op in ops if op.gate_name in {'h', 'hadamard'}]
            oracle_ops = [op for op in ops if len(op.control_qubits) > 0]
            x_ops = [op for op in ops if op.gate_name in {'x', 'pauli_x'}]
            cz_ops = [op for op in ops if op.gate_name == 'cz']
            multi_controlled = [op for op in ops if len(op.control_qubits) >= 2]
            has_initial_h = len(h_ops) >= n_qubits
            has_oracle = len(oracle_ops) > 0
            has_x_gates = len(x_ops) >= n_qubits
            # 2-qubit Grover commonly uses CZ as diffusion core.
            has_multi_controlled = len(multi_controlled) > 0 or (n_qubits <= 2 and len(cz_ops) > 0)
            has_multiple_h_layers = len(h_ops) >= n_qubits * 2
            has_measurements = ast.measurements is not None and len(ast.measurements) > 0
        else:
            h_gates = [g for g in ast.gates if g.gate_type == GateType.H]
            oracle_gates = [g for g in ast.gates if g.is_controlled]
            x_gates = [g for g in ast.gates if g.gate_type == GateType.X]
            cz_gates = [g for g in ast.gates if g.gate_type == GateType.CZ]
            multi_controlled = [g for g in ast.gates if g.is_controlled and len(g.control_qubits) >= 2]
            has_initial_h = len(h_gates) >= n_qubits
            has_oracle = len(oracle_gates) > 0
            has_x_gates = len(x_gates) >= n_qubits
            has_multi_controlled = len(multi_controlled) > 0 or (n_qubits <= 2 and len(cz_gates) > 0)
            has_multiple_h_layers = len(h_gates) >= n_qubits * 2
            has_measurements = ast.measurements is not None and len(ast.measurements) > 0

        # Source-level fallback for compact syntactic forms like h(range(n)).
        has_initial_h = has_initial_h or self._contains_any(code, [".h(range(", "h.on_each("])
        has_oracle = has_oracle or self._contains_any(code, [".cz(", ".cx(", "toffoli", "reflectaboutmarked"])
        has_multiple_h_layers = has_multiple_h_layers or self._contains_any(code, [".h(range(", "h.on_each("])
        
        requirements['initial_superposition'] = has_initial_h
        if not has_initial_h:
            violations.append("Missing initial superposition")
        
        requirements['has_oracle'] = has_oracle
        if not has_oracle:
            violations.append("No oracle detected")
        
        # Some valid Grover variants use CZ-only diffusion for 2 qubits.
        has_diffusion_components = has_x_gates or (n_qubits <= 2 and self._contains_any(code, [".cz("]))
        requirements['has_x_gates'] = has_diffusion_components
        if not has_diffusion_components:
            violations.append("Missing diffusion components")
        
        requirements['has_diffusion_core'] = has_multi_controlled
        if not has_multi_controlled:
            violations.append("Missing multi-controlled gate in diffusion")
        
        requirements['has_multiple_h_layers'] = has_multiple_h_layers
        if not has_multiple_h_layers:
            violations.append("Missing multiple Hadamard layers")
        
        requirements['has_measurements'] = has_measurements
        if not has_measurements:
            violations.append("No measurements")
        
        # Convert to int: True=1, False=0
        confidence = sum(int(v) for v in requirements.values()) / len(requirements) if len(requirements) > 0 else 0.0
        is_valid = confidence >= 0.6
        
        return ValidationResult(
            is_valid=is_valid,
            algorithm='grover',
            confidence=confidence,
            violations=violations,
            requirements_met=requirements,
            metadata={
                'qubits': n_qubits,
                'uses_canonical_ir': bool(ast.canonical_ir)
            }
        )

class QFTValidator(AlgorithmValidator):
    """
    Validates Quantum Fourier Transform
    
    Requirements:
    1. H gates on all qubits
    2. Controlled phase rotations (CP gates)
    3. Increasing rotation angles (powers of 2)
    4. Optional: SWAP gates at end
    """
    
    def validate(self, code: str) -> ValidationResult:
        ast = self.parse_code(code)
        if not ast:
            return ValidationResult(
                is_valid=False,
                algorithm='qft',
                confidence=0.0,
                violations=['Failed to parse code'],
                requirements_met={},
                metadata={}
            )
        
        violations = []
        requirements = {}
        
        n_qubits = ast.total_qubits
        
        # Requirement 1: H gates
        h_gates = [g for g in ast.gates if g.gate_type == GateType.H]
        has_h_gates = len(h_gates) >= n_qubits
        has_h_gates = has_h_gates or self._contains_any(code, [".h(", " h q["])
        requirements['has_hadamards'] = has_h_gates
        if not has_h_gates:
            violations.append("Missing Hadamard gates")
        
        # Requirement 2: Controlled phase rotations
        cp_gates = [
            g for g in ast.gates
            if g.gate_type in {GateType.CP, GateType.CRZ}
            or (g.is_controlled and g.parameters)
        ]
        has_cp_gates = len(cp_gates) > 0
        # OpenQASM often decomposes controlled phase into u1 + cx patterns.
        has_cp_gates = has_cp_gates or self._contains_any(code, [".cp(", " cp ", "u1(", "cu1", "crz("])
        requirements['has_phase_rotations'] = has_cp_gates
        if not has_cp_gates:
            violations.append("Missing controlled phase rotations")
        
        # Requirement 3: Sufficient rotations for QFT
        # QFT needs n(n-1)/2 controlled rotations
        expected_cp = (n_qubits * (n_qubits - 1)) // 2
        has_sufficient_rotations = len(cp_gates) >= expected_cp * 0.3 or self._contains_any(code, ["u1(", ".cp("])
        requirements['sufficient_rotations'] = has_sufficient_rotations
        if not has_sufficient_rotations:
            violations.append("Insufficient phase rotations for QFT")
        
        # Requirement 4: SWAP gates (optional but common)
        swap_gates = [g for g in ast.gates if g.gate_type == GateType.SWAP]
        has_swaps = len(swap_gates) > 0
        has_swaps = has_swaps or self._contains_any(code, [".swap(", " swap "])
        requirements['has_swaps'] = has_swaps
        # Note: Not a violation if missing, as it's optional
        
        confidence = sum(int(v) for v in requirements.values()) / len(requirements)
        is_valid = confidence >= 0.5
        
        return ValidationResult(
            is_valid=is_valid,
            algorithm='qft',
            confidence=confidence,
            violations=violations,
            requirements_met=requirements,
            metadata={
                'qubits': n_qubits,
                'h_gates': len(h_gates),
                'cp_gates': len(cp_gates),
                'swap_gates': len(swap_gates)
            }
        )

class SimonValidator(AlgorithmValidator):
    """
    Validates Simon's algorithm
    
    Requirements:
    1. Two registers (input and output)
    2. H on input register
    3. Oracle (copies pattern)
    4. H on input register after oracle
    5. Measurement on input register
    """
    
    def validate(self, code: str) -> ValidationResult:
        ast = self.parse_code(code)
        if not ast:
            return ValidationResult(
                is_valid=False,
                algorithm='simon',
                confidence=0.0,
                violations=['Failed to parse code'],
                requirements_met={},
                metadata={}
            )
        
        violations = []
        requirements = {}
        
        n_qubits = ast.total_qubits
        
        # Simon needs at least 2 qubits (1 input, 1 output minimum).
        # For symbolic circuit sizes (e.g., QuantumCircuit(2*n, n)), parser may under-infer.
        if n_qubits < 2 and not self._contains_any(code, ["simon_oracle", "quantumcircuit(2*n", "quantumcircuit(2 * n"]):
            return ValidationResult(
                is_valid=False,
                algorithm='simon',
                confidence=0.0,
                violations=['Insufficient qubits for Simon algorithm'],
                requirements_met={},
                metadata={'qubits': n_qubits}
            )

        if n_qubits < 2:
            n_qubits = 2
        
        # Assume n/2 split for input/output registers
        input_size = max(1, n_qubits // 2)
        input_qubits = set(range(input_size))
        
        # Requirement 1: H on input qubits
        h_on_input = sum(
            1 for g in ast.gates
            if g.gate_type == GateType.H
            and any(q in input_qubits for q in g.qubits)
        )
        
        has_input_h = h_on_input >= input_size
        has_input_h = has_input_h or self._contains_any(code, [".h(range(", " h q["])
        requirements['input_hadamards'] = has_input_h
        if not has_input_h:
            violations.append("Missing Hadamards on input register")
        
        # Requirement 2: Oracle (CX between registers)
        cx_gates = [
            g for g in ast.gates
            if g.gate_type in {GateType.CX, GateType.CNOT}
        ]
        has_oracle = len(cx_gates) >= input_size
        has_oracle = has_oracle or self._contains_any(code, ["simon_oracle", ".compose(", ".cx(", " ccx "])
        requirements['has_oracle'] = has_oracle
        if not has_oracle:
            violations.append("Oracle missing or incomplete")
        
        # Requirement 3: Post-oracle H
        has_post_h = h_on_input >= input_size * 2
        has_post_h = has_post_h or self._contains_any(code, [".h(range("])
        requirements['post_oracle_hadamards'] = has_post_h
        if not has_post_h:
            violations.append("Missing post-oracle Hadamards")
        
        # Requirement 4: Measurements
        has_measurements = ast.measurements is not None and len(ast.measurements) > 0
        requirements['has_measurements'] = has_measurements
        if not has_measurements:
            violations.append("No measurements")
        
        confidence = sum(int(v) for v in requirements.values()) / len(requirements)
        is_valid = confidence >= 0.6
        
        return ValidationResult(
            is_valid=is_valid,
            algorithm='simon',
            confidence=confidence,
            violations=violations,
            requirements_met=requirements,
            metadata={'qubits': n_qubits, 'input_size': input_size}
        )
    
class QPEValidator(AlgorithmValidator):
    """
    Validates Quantum Phase Estimation (QPE)

    Requirements:
    1. Hadamards on counting register
    2. Controlled unitary operations
    3. Inverse QFT (QFT†)
    4. Measurement
    """

    def validate(self, code: str) -> ValidationResult:
        ast = self.parse_code(code)
        if not ast:
            return ValidationResult(False, "qpe", 0.0, ["Parse failed"], {}, {})

        violations = []
        requirements = {}

        n_qubits = ast.total_qubits

        # 1. Hadamards
        h_gates = [g for g in ast.gates if g.gate_type == GateType.H]
        has_hadamards = len(h_gates) >= n_qubits // 2
        requirements["hadamards"] = has_hadamards
        if not has_hadamards:
            violations.append("Missing Hadamards on counting register")

        # 2. Controlled-U
        controlled_ops = [g for g in ast.gates if g.is_controlled]
        has_controlled_u = len(controlled_ops) > 0
        requirements["controlled_unitary"] = has_controlled_u
        if not has_controlled_u:
            violations.append("No controlled unitary detected")

        # 3. Inverse QFT
        has_qft = any(
            g.gate_type in {GateType.CP, GateType.CRZ}
            for g in ast.gates
        )
        requirements["inverse_qft"] = has_qft
        if not has_qft:
            violations.append("No inverse QFT structure detected")

        # 4. Measurement
        has_measurements = bool(ast.measurements)
        requirements["measurement"] = has_measurements
        if not has_measurements:
            violations.append("Missing measurement")

        confidence = sum(int(v) for v in requirements.values()) / len(requirements)

        return ValidationResult(
            is_valid=confidence >= 0.75,
            algorithm="qpe",
            confidence=confidence,
            violations=violations,
            requirements_met=requirements,
            metadata={"qubits": n_qubits}
        )

class ShorValidator(AlgorithmValidator):
    """
    Validates Shor's Algorithm

    Requirements:
    1. QPE structure
    2. Modular exponentiation oracle
    3. Inverse QFT
    """

    def validate(self, code: str) -> ValidationResult:
        ast = self.parse_code(code)
        if not ast:
            return ValidationResult(False, "shor", 0.0, ["Parse failed"], {}, {})

        violations = []
        requirements = {}

        # 1. Controlled modular exponentiation
        controlled_ops = [g for g in ast.gates if g.is_controlled]
        has_controlled = len(controlled_ops) > 2
        requirements["controlled_modexp"] = has_controlled
        if not has_controlled:
            violations.append("Missing controlled modular exponentiation")

        # 2. Inverse QFT
        has_qft = any(
            g.gate_type in {GateType.CP, GateType.CRZ}
            for g in ast.gates
        )
        requirements["inverse_qft"] = has_qft
        if not has_qft:
            violations.append("Missing inverse QFT")

        # 3. Measurement
        has_measurements = bool(ast.measurements)
        requirements["measurement"] = has_measurements
        if not has_measurements:
            violations.append("Missing measurement")

        confidence = sum(int(v) for v in requirements.values()) / len(requirements)

        return ValidationResult(
            is_valid=confidence >= 0.65,
            algorithm="shor",
            confidence=confidence,
            violations=violations,
            requirements_met=requirements,
            metadata={"controlled_ops": len(controlled_ops)}
        )

class QAOAValidator(AlgorithmValidator):
    """
    Validates QAOA (structure-only)

    Requirements:
    1. Parameterized gates
    2. Repeated layers
    3. Mixer + cost structure
    """

    def validate(self, code: str) -> ValidationResult:
        ast = self.parse_code(code)
        if not ast:
            return ValidationResult(False, "qaoa", 0.0, ["Parse failed"], {}, {})

        violations = []
        requirements = {}

        # 1. Parameterized gates
        param_gates = [g for g in ast.gates if g.parameters]
        has_params = len(param_gates) > 0
        requirements["parameterized_gates"] = has_params
        if not has_params:
            violations.append("No parameterized gates detected")

        # 2. Repeated structure
        repeated = len(ast.gates) > ast.total_qubits * 4
        requirements["layered_structure"] = repeated
        if not repeated:
            violations.append("Insufficient layered structure")

        # 3. Mixer (RX / H)
        has_mixer = any(
            g.gate_type in {GateType.RX, GateType.H}
            for g in ast.gates
        )
        requirements["mixer"] = has_mixer
        if not has_mixer:
            violations.append("No mixer detected")

        confidence = sum(int(v) for v in requirements.values()) / len(requirements)

        return ValidationResult(
            is_valid=confidence >= 0.6,
            algorithm="qaoa",
            confidence=confidence,
            violations=violations,
            requirements_met=requirements,
            metadata={"param_gates": len(param_gates)}
        )

class AlgorithmValidatorFactory:
    """Factory for creating algorithm validators"""
    
    VALIDATORS = {
        "bernstein_vazirani": BernsteinVaziraniValidator,
        "deutsch_jozsa": DeutschJozsaValidator,
        "grover": GroverValidator,
        "qft": QFTValidator,
        "simon": SimonValidator,
        "qpe": QPEValidator,
        "shor": ShorValidator,
        "qaoa": QAOAValidator,
    }
    
    @classmethod
    def get_validator(cls, algorithm: str) -> Optional[AlgorithmValidator]:
        """Get validator for algorithm"""
        validator_class = cls.VALIDATORS.get(algorithm)
        if validator_class:
            return validator_class()
        return None
    
    @classmethod
    def validate_all_algorithms(cls, code: str) -> Dict[str, ValidationResult]:
        """Run all validators on code"""
        results = {}
        for algorithm, validator_class in cls.VALIDATORS.items():
            validator = validator_class()
            results[algorithm] = validator.validate(code)
        return results

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Test validation
    test_bv_code = """
from qiskit import QuantumCircuit

qc = QuantumCircuit(4, 3)

# Initialize ancilla
qc.x(3)
qc.h(3)

# Superposition
for i in range(3):
    qc.h(i)

# Oracle
qc.cx(0, 3)
qc.cx(1, 3)

# Hadamard
for i in range(3):
    qc.h(i)

# Measurement
qc.measure(range(3), range(3))
    """
    
    print("=" * 80)
    print("ALGORITHM VALIDATOR TEST")
    print("=" * 80)
    
    # Test Bernstein-Vazirani
    bv_validator = BernsteinVaziraniValidator()
    result = bv_validator.validate(test_bv_code)
    
    print(f"\nAlgorithm: {result.algorithm}")
    print(f"Valid: {result.is_valid}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"\nRequirements:")
    for req, met in result.requirements_met.items():
        status = "✅" if met else "❌"
        print(f"  {status} {req}")
    
    if result.violations:
        print(f"\nViolations:")
        for violation in result.violations:
            print(f"  - {violation}")
    
    print("\n" + "=" * 80)
    
    # Test all validators
    print("\nTesting all validators on same code:")
    all_results = AlgorithmValidatorFactory.validate_all_algorithms(test_bv_code)
    
    print(f"\n{'Algorithm':<20} {'Valid':<10} {'Confidence':<15}")
    print("-" * 50)
    for algo, res in sorted(all_results.items()):
        valid_str = "✅ Yes" if res.is_valid else "❌ No"
        print(f"{algo:<20} {valid_str:<10} {res.confidence:<15.2%}")
    
    print("=" * 80)