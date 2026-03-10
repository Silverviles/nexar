"""Cirq parser using Python AST extraction."""
import ast
from typing import Any, Dict, List, Optional

from .base_parser import BaseParser
from models.unified_ast import GateType, MeasurementNode, QuantumGateNode, QuantumRegisterNode


class CirqParser(BaseParser):
    """Parser for Python programs using Cirq APIs."""

    def __init__(self):
        super().__init__()
        self.tree: Optional[ast.AST] = None
        self.default_qubit_count: int = 0
        self.gate_mapping = {
            "h": GateType.H,
            "x": GateType.X,
            "y": GateType.Y,
            "z": GateType.Z,
            "rx": GateType.RX,
            "ry": GateType.RY,
            "rz": GateType.RZ,
            "cnot": GateType.CNOT,
            "cx": GateType.CX,
            "cz": GateType.CZ,
            "swap": GateType.SWAP,
            "ccx": GateType.TOFFOLI,
            "toffoli": GateType.TOFFOLI,
            "measure": GateType.MEASURE,
        }

    def parse(self, code: str) -> Dict[str, Any]:
        self.code = code
        self.lines = code.splitlines()
        self.default_qubit_count = 0

        try:
            self.tree = ast.parse(code)
        except SyntaxError:
            self.tree = None

        flow_meta = self.extract_python_control_flow_metadata(code)

        return {
            "imports": self.extract_imports(),
            "registers": self.extract_registers(),
            "gates": self.extract_quantum_operations(),
            "measurements": self.extract_measurements(),
            "functions": self.extract_functions(code),
            "metadata": {
                "lines_of_code": self.count_lines(code),
                "loop_count": flow_meta.get("loop_count", 0),
                "conditional_count": flow_meta.get("conditional_count", 0),
                "nesting_depth": flow_meta.get("nesting_depth", 0),
                "control_flow_nesting_depth": flow_meta.get("control_flow_nesting_depth", 0),
                "structural_nesting_depth": flow_meta.get("structural_nesting_depth", flow_meta.get("nesting_depth", 0)),
                "line_loop_multiplier": flow_meta.get("line_loop_multiplier", {}),
            },
        }

    def extract_imports(self) -> List[str]:
        imports = []
        for line in self.lines:
            stripped = line.strip()
            if stripped.startswith("import cirq") or stripped.startswith("from cirq"):
                imports.append(stripped)
        return imports

    def extract_registers(self) -> Dict[str, Any]:
        quantum_regs: List[QuantumRegisterNode] = []
        qubit_count = 0

        if self.tree is not None:
            for node in ast.walk(self.tree):
                if not isinstance(node, ast.Assign):
                    continue
                if not isinstance(node.value, ast.Call):
                    continue

                call = node.value
                func = call.func

                # cirq.LineQubit.range(n)
                if (
                    isinstance(func, ast.Attribute)
                    and func.attr == "range"
                    and isinstance(func.value, ast.Attribute)
                    and isinstance(func.value.value, ast.Name)
                    and func.value.value.id == "cirq"
                    and func.value.attr == "LineQubit"
                    and call.args
                    and isinstance(call.args[0], ast.Constant)
                    and isinstance(call.args[0].value, int)
                ):
                    qubit_count = max(qubit_count, int(call.args[0].value))

                # [cirq.LineQubit(i) for i in range(n)]
                if isinstance(node.value, ast.ListComp):
                    for gen in node.value.generators:
                        if (
                            isinstance(gen.iter, ast.Call)
                            and isinstance(gen.iter.func, ast.Name)
                            and gen.iter.func.id == "range"
                            and gen.iter.args
                            and isinstance(gen.iter.args[0], ast.Constant)
                            and isinstance(gen.iter.args[0].value, int)
                        ):
                            qubit_count = max(qubit_count, int(gen.iter.args[0].value))

                # direct single qubit creation
                if (
                    isinstance(func, ast.Attribute)
                    and isinstance(func.value, ast.Name)
                    and func.value.id == "cirq"
                    and func.attr in {"LineQubit", "NamedQubit", "GridQubit"}
                ):
                    qubit_count = max(qubit_count, qubit_count + 1)

        # If qubit_count is still 0, try to infer from gate usage
        if qubit_count == 0:
            qubit_count = self._infer_qubit_count_from_gates()

        self.default_qubit_count = qubit_count
        
        quantum_regs.append(QuantumRegisterNode(name="qubits", size=qubit_count, line_number=None))
        return {"quantum": quantum_regs, "classical": []}

    def extract_quantum_operations(self) -> List[QuantumGateNode]:
        gates: List[QuantumGateNode] = []
        if self.tree is None:
            return gates

        for node in ast.walk(self.tree):
            if not isinstance(node, ast.Call):
                continue

            op_name = self._resolve_cirq_call_name(node.func)
            if op_name is None:
                continue
            op_name = op_name.lower()

            if op_name not in self.gate_mapping or op_name == "measure":
                continue

            gate_type = self.gate_mapping[op_name]
            qubits = self._extract_qubit_indices(node.args)

            controls = []
            targets = qubits
            if op_name in {"cnot", "cx", "cz"} and len(qubits) >= 2:
                controls = [qubits[0]]
                targets = [qubits[-1]]
            elif op_name in {"ccx", "toffoli"} and len(qubits) >= 3:
                controls = qubits[:-1]
                targets = [qubits[-1]]

            # Skip malformed gate nodes that carry no qubit information.
            if len(targets) == 0 and len(controls) == 0:
                continue

            gates.append(
                QuantumGateNode(
                    gate_type=gate_type,
                    qubits=targets,
                    control_qubits=controls,
                    is_controlled=bool(controls),
                    line_number=node.lineno,
                )
            )

        return gates

    def extract_measurements(self) -> List[MeasurementNode]:
        out: List[MeasurementNode] = []
        if self.tree is None:
            return out

        for node in ast.walk(self.tree):
            if not isinstance(node, ast.Call):
                continue
            op_name = self._resolve_cirq_call_name(node.func)
            if op_name is None or op_name.lower() != "measure":
                continue

            q_idxs = []
            for arg in node.args:
                if isinstance(arg, ast.Starred):
                    # measure(*qubits) -> unknown exact mapping statically.
                    continue
                idx = self._extract_qubit_index(arg)
                if idx is not None:
                    q_idxs.append(idx)

            out.append(
                MeasurementNode(
                    quantum_register="qubits",
                    classical_register="measurements",
                    qubit_indices=q_idxs,
                    classical_indices=list(range(len(q_idxs))),
                    line_number=node.lineno,
                )
            )

        return out

    def _resolve_cirq_call_name(self, func: ast.AST) -> Optional[str]:
        # cirq.H(...)
        if (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id == "cirq"
        ):
            return func.attr

        # cirq.H.on(...)
        if (
            isinstance(func, ast.Attribute)
            and func.attr == "on"
            and isinstance(func.value, ast.Attribute)
            and isinstance(func.value.value, ast.Name)
            and func.value.value.id == "cirq"
        ):
            return func.value.attr

        # cirq.H.on_each(...)
        if (
            isinstance(func, ast.Attribute)
            and func.attr == "on_each"
            and isinstance(func.value, ast.Attribute)
            and isinstance(func.value.value, ast.Name)
            and func.value.value.id == "cirq"
        ):
            return func.value.attr

        return None

    def _extract_qubit_index(self, node: ast.AST) -> Optional[int]:
        if isinstance(node, ast.Starred):
            return None

        if isinstance(node, ast.Name):
            # Fallback for symbolic names like output_qubit/input_qubits in examples.
            return 0

        # qubits[3]
        if isinstance(node, ast.Subscript):
            idx_node = node.slice.value if isinstance(node.slice, ast.Index) else node.slice
            if isinstance(idx_node, ast.Constant) and isinstance(idx_node.value, int):
                return int(idx_node.value)

        # LineQubit(3)
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "cirq"
            and node.func.attr == "LineQubit"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, int)
        ):
            return int(node.args[0].value)

        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return int(node.value)

        return None

    def _extract_qubit_indices(self, args: List[ast.AST]) -> List[int]:
        """Extract qubit indices from call args including starred sequences."""
        indices: List[int] = []
        for arg in args:
            if isinstance(arg, ast.Starred):
                if self.default_qubit_count > 0:
                    indices.extend(list(range(self.default_qubit_count)))
                else:
                    indices.append(0)
                continue

            idx = self._extract_qubit_index(arg)
            if idx is not None:
                indices.append(idx)

        # Deduplicate while preserving order.
        seen = set()
        deduped: List[int] = []
        for idx in indices:
            if idx not in seen:
                seen.add(idx)
                deduped.append(idx)
        return deduped
    
    def _infer_qubit_count_from_gates(self) -> int:
        """
        Infer qubit count from gate operations when register declaration uses variables.
        Falls back to analyzing which qubit indices are used in gates.
        """
        if self.tree is None:
            return 0
        
        max_qubit_index = -1
        
        for node in ast.walk(self.tree):
            if not isinstance(node, ast.Call):
                continue
            
            # Check if it's a Cirq gate operation
            op_name = self._resolve_cirq_call_name(node.func)
            if op_name is None:
                continue
            
            # Extract qubit indices from this gate
            for arg in node.args:
                if isinstance(arg, ast.Starred):
                    # *qubits - can't determine statically, use a reasonable default
                    max_qubit_index = max(max_qubit_index, 2)
                    continue
                idx = self._extract_qubit_index(arg)
                if idx is not None:
                    max_qubit_index = max(max_qubit_index, idx)
        
        # Return qubit count (max_index + 1) or 0 if no qubits found
        return max_qubit_index + 1 if max_qubit_index >= 0 else 0
