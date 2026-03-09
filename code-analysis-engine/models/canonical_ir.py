"""
Canonical Quantum IR models.

These models capture semantic circuit intent, operation dependencies,
interaction topology, and control-flow context in a language-agnostic format.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class IRExecutionContext(BaseModel):
    """Execution context for an operation inside the source program."""

    loop_iterations: int = 1
    conditional: Optional[str] = None
    source_framework: Optional[str] = None
    source_snippet: Optional[str] = None


class IROperation(BaseModel):
    """One semantically meaningful operation in Canonical IR."""

    op_id: str
    op_type: str  # gate | measure | barrier | reset | classical
    gate_name: Optional[str] = None

    target_qubits: List[int] = Field(default_factory=list)
    control_qubits: List[int] = Field(default_factory=list)
    classical_targets: List[int] = Field(default_factory=list)

    parameters: List[float] = Field(default_factory=list)
    semantic_tags: List[str] = Field(default_factory=list)

    dependencies: List[str] = Field(default_factory=list)
    moment_index: Optional[int] = None
    line_number: Optional[int] = None

    execution: IRExecutionContext = Field(default_factory=IRExecutionContext)


class CanonicalQuantumIR(BaseModel):
    """Language-neutral semantic IR used by analyzers and ML feature extraction."""

    source_language: str

    qubit_count: int = 0
    classical_bit_count: int = 0

    operations: List[IROperation] = Field(default_factory=list)
    dependency_graph: Dict[str, List[str]] = Field(default_factory=dict)
    qubit_interactions: Dict[int, List[int]] = Field(default_factory=dict)

    loop_count: int = 0
    conditional_count: int = 0
    max_nesting_depth: int = 0

    metadata: Dict[str, Any] = Field(default_factory=dict)

    def operation_count(self) -> int:
        return len(self.operations)

    def measurement_count(self) -> int:
        return sum(1 for op in self.operations if op.op_type == "measure")

    def gate_count(self) -> int:
        return sum(1 for op in self.operations if op.op_type == "gate")

    def entangling_pair_count(self) -> int:
        pairs = set()
        for op in self.operations:
            touched = sorted(set(op.control_qubits + op.target_qubits))
            if len(touched) < 2:
                continue
            for i in range(len(touched)):
                for j in range(i + 1, len(touched)):
                    pairs.add((touched[i], touched[j]))
        return len(pairs)
