"""
Canonical IR builder.

Converts parsed gate/register information into a semantic CanonicalQuantumIR
with explicit dependencies and qubit interaction graph.
"""
from typing import Dict, List, Optional

from models.canonical_ir import CanonicalQuantumIR, IROperation
from models.unified_ast import GateType, MeasurementNode, QuantumGateNode, UnifiedAST


ENTANGLING_GATES = {
    GateType.CNOT,
    GateType.CX,
    GateType.CZ,
    GateType.SWAP,
    GateType.TOFFOLI,
    GateType.FREDKIN,
    GateType.CSWAP,
}

SUPERPOSITION_GATES = {
    GateType.H,
    GateType.RX,
    GateType.RY,
}


class CanonicalIRBuilder:
    """Build CanonicalQuantumIR from UnifiedAST + parser metadata."""

    def build(self, unified_ast: UnifiedAST, metadata: Optional[Dict] = None) -> CanonicalQuantumIR:
        metadata = metadata or {}

        line_loop_multiplier = metadata.get("line_loop_multiplier", {})
        qubit_last_op: Dict[int, str] = {}
        operations: List[IROperation] = []

        # Gate operations.
        for index, gate in enumerate(unified_ast.gates):
            op_id = f"g{index}"
            touched_qubits = sorted(set((gate.control_qubits or []) + (gate.qubits or [])))
            deps = self._deps_for_qubits(touched_qubits, qubit_last_op)

            semantic_tags = []
            if gate.gate_type in SUPERPOSITION_GATES:
                semantic_tags.append("creates_superposition")
            if gate.gate_type in ENTANGLING_GATES or gate.is_controlled:
                semantic_tags.append("creates_or_propagates_entanglement")

            execution_loops = 1
            if gate.line_number is not None:
                execution_loops = max(int(line_loop_multiplier.get(str(gate.line_number), 1)), 1)

            op = IROperation(
                op_id=op_id,
                op_type="gate",
                gate_name=gate.gate_type.value,
                target_qubits=list(gate.qubits),
                control_qubits=list(gate.control_qubits),
                parameters=[float(p) for p in gate.parameters if isinstance(p, (int, float))],
                semantic_tags=semantic_tags,
                dependencies=deps,
                line_number=gate.line_number,
                execution={
                    "loop_iterations": execution_loops,
                    "source_framework": unified_ast.source_language,
                },
            )
            operations.append(op)

            for qubit in touched_qubits:
                qubit_last_op[qubit] = op_id

        # Measurement operations.
        for m_index, measurement in enumerate(unified_ast.measurements):
            op_id = f"m{m_index}"
            qubits = self._measurement_qubits(measurement, unified_ast.total_qubits)
            deps = self._deps_for_qubits(qubits, qubit_last_op)

            op = IROperation(
                op_id=op_id,
                op_type="measure",
                gate_name="measurement",
                target_qubits=qubits,
                classical_targets=list(measurement.classical_indices),
                semantic_tags=["measurement"],
                dependencies=deps,
                line_number=measurement.line_number,
                execution={"source_framework": unified_ast.source_language},
            )
            operations.append(op)

            for qubit in qubits:
                qubit_last_op[qubit] = op_id

        dependency_graph = {op.op_id: list(op.dependencies) for op in operations}
        interactions = self._build_qubit_interactions(operations)

        return CanonicalQuantumIR(
            source_language=unified_ast.source_language,
            qubit_count=unified_ast.total_qubits,
            classical_bit_count=unified_ast.total_classical_bits,
            operations=operations,
            dependency_graph=dependency_graph,
            qubit_interactions=interactions,
            loop_count=metadata.get("loop_count", 0),
            conditional_count=metadata.get("conditional_count", 0),
            max_nesting_depth=metadata.get("control_flow_nesting_depth", metadata.get("nesting_depth", 0)),
            metadata={
                "lines_of_code": metadata.get("lines_of_code", 0),
                "function_count": metadata.get("function_count", 0),
                "control_flow_nesting_depth": metadata.get("control_flow_nesting_depth", metadata.get("nesting_depth", 0)),
                "structural_nesting_depth": metadata.get("structural_nesting_depth", metadata.get("nesting_depth", 0)),
            },
        )

    def _deps_for_qubits(self, qubits: List[int], qubit_last_op: Dict[int, str]) -> List[str]:
        deps = {qubit_last_op[q] for q in qubits if q in qubit_last_op}
        return sorted(deps)

    def _measurement_qubits(self, measurement: MeasurementNode, total_qubits: int) -> List[int]:
        if measurement.qubit_indices:
            return sorted(set(measurement.qubit_indices))
        if measurement.quantum_register == "ALL":
            return list(range(total_qubits))
        return []

    def _build_qubit_interactions(self, operations: List[IROperation]) -> Dict[int, List[int]]:
        graph: Dict[int, set] = {}
        for op in operations:
            touched = sorted(set(op.control_qubits + op.target_qubits))
            if len(touched) < 2:
                continue
            for src in touched:
                graph.setdefault(src, set())
                for dst in touched:
                    if src != dst:
                        graph[src].add(dst)
        return {k: sorted(v) for k, v in graph.items()}
