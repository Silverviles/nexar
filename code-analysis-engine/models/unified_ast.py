"""
Unified AST and compatibility models.
"""
from typing import Any, Dict, List, Optional, Set
from enum import Enum
from pydantic import BaseModel, Field

from models.canonical_ir import CanonicalQuantumIR


class NodeType(str, Enum):
    """AST node types used in language-specific parse outputs."""

    PROGRAM = "program"
    IMPORT = "import"
    FUNCTION = "function"
    CLASS = "class"
    QUANTUM_CIRCUIT = "quantum_circuit"
    QUANTUM_REGISTER = "quantum_register"
    CLASSICAL_REGISTER = "classical_register"
    QUANTUM_GATE = "quantum_gate"
    MEASUREMENT = "measurement"
    LOOP = "loop"
    CONDITIONAL = "conditional"
    VARIABLE = "variable"
    EXPRESSION = "expression"


class GateType(str, Enum):
    """Normalized gate vocabulary used across all parsers and analyzers."""

    H = "hadamard"
    X = "pauli_x"
    Y = "pauli_y"
    Z = "pauli_z"
    S = "s_gate"
    T = "t_gate"
    RX = "rotation_x"
    RY = "rotation_y"
    RZ = "rotation_z"

    CNOT = "cnot"
    CX = "cx"
    CZ = "cz"
    SWAP = "swap"

    TOFFOLI = "toffoli"
    FREDKIN = "fredkin"

    CH = "controlled_h"
    CY = "controlled_y"
    CP = "controlled_phase"
    CRX = "controlled_rx"
    CRY = "controlled_ry"
    CRZ = "controlled_rz"
    CU = "controlled_u"
    CU1 = "controlled_u1"
    CU3 = "controlled_u3"
    CSWAP = "controlled_swap"

    MEASURE = "measurement"
    BARRIER = "barrier"
    RESET = "reset"
    CUSTOM = "custom"


class ASTNode(BaseModel):
    """Generic node used for lightweight control-flow/function metadata."""

    node_type: NodeType
    name: Optional[str] = None
    line_number: Optional[int] = None
    children: List["ASTNode"] = Field(default_factory=list)
    attributes: Dict[str, Any] = Field(default_factory=dict)


class QuantumRegisterNode(BaseModel):
    name: str
    size: int
    line_number: Optional[int] = None


class ClassicalRegisterNode(BaseModel):
    name: str
    size: int
    line_number: Optional[int] = None


class QuantumGateNode(BaseModel):
    gate_type: GateType
    qubits: List[int]
    parameters: List[float] = Field(default_factory=list)
    line_number: Optional[int] = None
    is_controlled: bool = False
    control_qubits: List[int] = Field(default_factory=list)


class MeasurementNode(BaseModel):
    quantum_register: str
    classical_register: str
    qubit_indices: List[int]
    classical_indices: List[int]
    line_number: Optional[int] = None


class ControlFlowNode(BaseModel):
    flow_type: str
    condition: Optional[str] = None
    body: List[ASTNode] = Field(default_factory=list)
    line_number: Optional[int] = None


class UnifiedAST(BaseModel):
    """Compatibility AST plus semantic Canonical IR payload."""

    source_language: str
    quantum_registers: List[QuantumRegisterNode] = Field(default_factory=list)
    classical_registers: List[ClassicalRegisterNode] = Field(default_factory=list)
    gates: List[QuantumGateNode] = Field(default_factory=list)
    measurements: List[MeasurementNode] = Field(default_factory=list)
    control_flows: List[ControlFlowNode] = Field(default_factory=list)
    imports: List[str] = Field(default_factory=list)
    functions: List[ASTNode] = Field(default_factory=list)
    root: Optional[ASTNode] = None

    canonical_ir: Optional[CanonicalQuantumIR] = None

    total_qubits: int = 0
    total_classical_bits: int = 0
    total_gates: int = 0

    def get_gate_types(self) -> Set[GateType]:
        if self.canonical_ir:
            gate_names = {
                op.gate_name
                for op in self.canonical_ir.operations
                if op.op_type == "gate" and op.gate_name
            }
            return {gt for gt in GateType if gt.value in gate_names}
        return {gate.gate_type for gate in self.gates}

    def get_entangling_gates(self) -> List[QuantumGateNode]:
        entangling = {
            GateType.CNOT,
            GateType.CX,
            GateType.CZ,
            GateType.SWAP,
            GateType.TOFFOLI,
            GateType.FREDKIN,
        }
        return [gate for gate in self.gates if gate.gate_type in entangling]

    def get_single_qubit_gates(self) -> List[QuantumGateNode]:
        single_qubit = {
            GateType.H,
            GateType.X,
            GateType.Y,
            GateType.Z,
            GateType.S,
            GateType.T,
            GateType.RX,
            GateType.RY,
            GateType.RZ,
        }
        return [gate for gate in self.gates if gate.gate_type in single_qubit]

    def calculate_circuit_depth(self) -> int:
        if self.canonical_ir and self.canonical_ir.operations:
            by_id = {op.op_id: op for op in self.canonical_ir.operations}
            memo: Dict[str, int] = {}

            def depth_for(op_id: str) -> int:
                if op_id in memo:
                    return memo[op_id]
                op = by_id.get(op_id)
                if op is None or not op.dependencies:
                    memo[op_id] = 1
                    return 1
                memo[op_id] = 1 + max(depth_for(dep) for dep in op.dependencies if dep in by_id)
                return memo[op_id]

            return max(depth_for(op_id) for op_id in by_id) if by_id else 0
        return len(self.gates)

    def has_superposition(self) -> bool:
        if self.canonical_ir:
            return any(
                "creates_superposition" in op.semantic_tags
                for op in self.canonical_ir.operations
                if op.op_type == "gate"
            )
        superposition_gates = {GateType.H, GateType.RX, GateType.RY}
        return any(gate.gate_type in superposition_gates for gate in self.gates)

    def has_entanglement(self) -> bool:
        if self.canonical_ir:
            return any(
                "creates_or_propagates_entanglement" in op.semantic_tags
                for op in self.canonical_ir.operations
                if op.op_type == "gate"
            )
        return len(self.get_entangling_gates()) > 0

    def to_ir(self) -> Dict[str, Any]:
        """Serialize semantic IR for datasets and downstream training."""
        if self.canonical_ir is not None:
            return self.canonical_ir.dict()

        # Backward compatible fallback when IR wasn't built.
        return {
            "source_language": self.source_language,
            "qubit_count": self.total_qubits,
            "classical_bit_count": self.total_classical_bits,
            "operations": [
                {
                    "op_type": "gate",
                    "gate_name": gate.gate_type.value,
                    "target_qubits": gate.qubits,
                    "control_qubits": gate.control_qubits,
                    "parameters": gate.parameters,
                    "line_number": gate.line_number,
                }
                for gate in self.gates
            ],
            "metadata": {"legacy": True},
        }
    
    @classmethod
    def from_ir(cls, ir_dict: Dict[str, Any]) -> "UnifiedAST":
        """Reconstruct UnifiedAST from IR dictionary for dataset loading."""
        # Reconstruct canonical IR if present
        canonical_ir = None
        if "operations" in ir_dict and not ir_dict.get("metadata", {}).get("legacy"):
            try:
                from models.canonical_ir import CanonicalQuantumIR, IROperation
                canonical_ir = CanonicalQuantumIR(
                    source_language=ir_dict.get("source_language", "unknown"),
                    qubit_count=ir_dict.get("qubit_count", 0),
                    classical_bit_count=ir_dict.get("classical_bit_count", 0),
                    operations=[
                        IROperation(**op) for op in ir_dict.get("operations", [])
                    ]
                )
            except Exception:
                pass  # Fall back to legacy gate reconstruction
        
        # Reconstruct gates list from operations
        gates = []
        for op in ir_dict.get("operations", []):
            if op.get("op_type") == "gate":
                try:
                    gate_name = op.get("gate_name", "custom")
                    # Map gate name to GateType
                    gate_type = None
                    for gt in GateType:
                        if gt.value == gate_name:
                            gate_type = gt
                            break
                    if gate_type is None:
                        gate_type = GateType.CUSTOM
                    
                    gate = QuantumGateNode(
                        gate_type=gate_type,
                        qubits=op.get("target_qubits", []),
                        parameters=op.get("parameters", []),
                        line_number=op.get("line_number"),
                        is_controlled=len(op.get("control_qubits", [])) > 0,
                        control_qubits=op.get("control_qubits", [])
                    )
                    gates.append(gate)
                except Exception:
                    continue  # Skip malformed gates
        
        return cls(
            source_language=ir_dict.get("source_language", "unknown"),
            gates=gates,
            canonical_ir=canonical_ir,
            total_qubits=ir_dict.get("qubit_count", 0),
            total_classical_bits=ir_dict.get("classical_bit_count", 0),
            total_gates=len(gates)
        )


ASTNode.update_forward_refs() 