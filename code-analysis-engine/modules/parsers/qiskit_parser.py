"""Qiskit parser using Python AST extraction for circuit semantics."""
import ast
from typing import Any, Dict, List, Optional

from .base_parser import BaseParser
from models.unified_ast import (
    ClassicalRegisterNode,
    GateType,
    MeasurementNode,
    QuantumGateNode,
    QuantumRegisterNode,
)


class QiskitParser(BaseParser):
    """Parser for Python programs that build Qiskit circuits."""

    def __init__(self):
        super().__init__()
        self.tree: Optional[ast.AST] = None
        self.circuit_vars: set = set()
        self.register_sizes: Dict[str, int] = {}
        self.symbol_table: Dict[str, Any] = {}
        self.loop_ranges: Dict[str, int] = {}
        self.gate_mapping = {
            "h": GateType.H,
            "x": GateType.X,
            "y": GateType.Y,
            "z": GateType.Z,
            "s": GateType.S,
            "t": GateType.T,
            "rx": GateType.RX,
            "ry": GateType.RY,
            "rz": GateType.RZ,
            "cx": GateType.CX,
            "cnot": GateType.CNOT,
            "cz": GateType.CZ,
            "swap": GateType.SWAP,
            "ccx": GateType.TOFFOLI,
            "toffoli": GateType.TOFFOLI,
            "ch": GateType.CH,
            "cy": GateType.CY,
            "cp": GateType.CP,
            "crx": GateType.CRX,
            "cry": GateType.CRY,
            "crz": GateType.CRZ,
            "cu": GateType.CU,
            "cu1": GateType.CU1,
            "cu3": GateType.CU3,
            "cswap": GateType.CSWAP,
            "barrier": GateType.BARRIER,
            "reset": GateType.RESET,
            "measure": GateType.MEASURE,
        }

    def parse(self, code: str) -> Dict[str, Any]:
        self.code = code
        self.lines = code.splitlines()
        self.circuit_vars = set()
        self.register_sizes = {}
        self.symbol_table = {}
        self.loop_ranges = {}

        try:
            self.tree = ast.parse(code)
        except SyntaxError:
            self.tree = None

        if self.tree is not None:
            self._build_symbol_table()
            self._collect_loop_ranges()

        flow_meta = self.extract_python_control_flow_metadata(code)

        parsed = {
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
        return parsed

    def extract_imports(self) -> List[str]:
        imports = []
        for line in self.lines:
            stripped = line.strip()
            if stripped.startswith("import qiskit") or stripped.startswith("from qiskit"):
                imports.append(stripped)
        return imports

    def extract_registers(self) -> Dict[str, Any]:
        quantum_regs: List[QuantumRegisterNode] = []
        classical_regs: List[ClassicalRegisterNode] = []

        if self.tree is None:
            return {"quantum": quantum_regs, "classical": classical_regs}

        for node in ast.walk(self.tree):
            if not isinstance(node, ast.Assign):
                continue
            if not isinstance(node.value, ast.Call):
                continue
            if not isinstance(node.value.func, ast.Name):
                continue

            ctor_name = node.value.func.id
            target_name = self._assign_target_name(node.targets)
            if target_name is None:
                continue

            if ctor_name == "QuantumRegister":
                size = self._eval_int_expr(node.value.args[0]) if node.value.args else 0
                size = size if size is not None else 0
                reg_name = self._const_str(node.value.args[1]) if len(node.value.args) > 1 else target_name
                quantum_regs.append(
                    QuantumRegisterNode(name=reg_name or target_name, size=size, line_number=node.lineno)
                )
                self.register_sizes[target_name] = size

            elif ctor_name == "ClassicalRegister":
                size = self._eval_int_expr(node.value.args[0]) if node.value.args else 0
                size = size if size is not None else 0
                reg_name = self._const_str(node.value.args[1]) if len(node.value.args) > 1 else target_name
                classical_regs.append(
                    ClassicalRegisterNode(name=reg_name or target_name, size=size, line_number=node.lineno)
                )
                self.register_sizes[target_name] = size

            elif ctor_name == "QuantumCircuit":
                self.circuit_vars.add(target_name)
                q_count = 0
                c_count = 0
                if len(node.value.args) >= 1:
                    q_count = self._eval_int_expr(node.value.args[0])
                    q_count = q_count if q_count is not None else 0
                if len(node.value.args) >= 2:
                    c_count = self._eval_int_expr(node.value.args[1])
                    c_count = c_count if c_count is not None else 0

                if q_count > 0:
                    quantum_regs.append(QuantumRegisterNode(name="q", size=q_count, line_number=node.lineno))
                    self.register_sizes["q"] = q_count
                if c_count > 0:
                    classical_regs.append(ClassicalRegisterNode(name="c", size=c_count, line_number=node.lineno))
                    self.register_sizes["c"] = c_count

        if not quantum_regs:
            quantum_regs.append(QuantumRegisterNode(name="q", size=0, line_number=None))
        
        # If all quantum registers have size 0, try to infer from gate usage
        if all(reg.size == 0 for reg in quantum_regs):
            inferred_size = self._infer_qubit_count_from_gates()
            if inferred_size > 0:
                quantum_regs = [QuantumRegisterNode(name="q", size=inferred_size, line_number=None)]

        return {"quantum": quantum_regs, "classical": classical_regs}

    def extract_quantum_operations(self) -> List[QuantumGateNode]:
        gates: List[QuantumGateNode] = []
        if self.tree is None:
            return gates

        # Instead of ast.walk, traverse tree with loop context
        self._extract_gates_with_loop_expansion(self.tree, gates, {})
        return gates

    def _extract_gates_with_loop_expansion(self, node: ast.AST, gates: List[QuantumGateNode], loop_ctx: Dict[str, int]):
        """
        Recursively traverse AST and expand gates inside for loops.
        
        Args:
            node: Current AST node
            gates: List to append extracted gates
            loop_ctx: Dict mapping loop variables to their current values
        """
        if isinstance(node, ast.For):
            # Check if this is a simple for i in range(n) loop
            if isinstance(node.target, ast.Name) and isinstance(node.iter, ast.Call):
                if isinstance(node.iter.func, ast.Name) and node.iter.func.id == "range":
                    # Extract the range values
                    range_values = self._extract_range_indices(node.iter)
                    if range_values:
                        # Expand the loop body for each iteration
                        loop_var = node.target.id
                        for val in range_values:
                            new_ctx = loop_ctx.copy()
                            new_ctx[loop_var] = val
                            # Process loop body with this value
                            for child in node.body:
                                self._extract_gates_with_loop_expansion(child, gates, new_ctx)
                        return  # Don't process children again
        
        # Check if this is a gate call
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            owner = node.func.value
            if isinstance(owner, ast.Name) and owner.id in self.circuit_vars:
                gate_name = node.func.attr.lower()
                if gate_name in self.gate_mapping and gate_name not in {"measure", "measure_all"}:
                    gate_type = self.gate_mapping[gate_name]
                    qubits, controls = self._extract_gate_qubits_with_context(gate_name, node.args, loop_ctx)
                    parameters = self._extract_gate_params(gate_name, node.args)

                    gates.append(
                        QuantumGateNode(
                            gate_type=gate_type,
                            qubits=qubits,
                            control_qubits=controls,
                            is_controlled=bool(controls),
                            parameters=parameters,
                            line_number=node.lineno,
                        )
                    )
                    return  # Don't recurse into gate call args
        
        # Recurse into children
        for child in ast.iter_child_nodes(node):
            self._extract_gates_with_loop_expansion(child, gates, loop_ctx)

    # Number of leading rotation-parameter args to skip before qubit args.
    # Qiskit API: circuit.ry(theta, qubit), circuit.cx(ctrl, tgt), etc.
    _GATE_PARAM_COUNTS: Dict[str, int] = {
        "rx": 1, "ry": 1, "rz": 1,
        "cp": 1, "crx": 1, "cry": 1, "crz": 1, "cu1": 1,
        "cu": 4, "cu3": 3,
    }

    def _extract_gate_qubits_with_context(self, gate_name: str, args: List[ast.AST], loop_ctx: Dict[str, int]) -> (List[int], List[int]):
        """Extract qubit indices with loop context for variable resolution."""
        # Skip leading parameter args (e.g. rotation angles) so they are not
        # mistakenly treated as qubit indices.
        n_params = self._GATE_PARAM_COUNTS.get(gate_name, 0)
        qubit_indices: List[int] = []
        for arg in args[n_params:]:
            qubit_indices.extend(self._extract_index_list_with_context(arg, loop_ctx))

        controlled_names = {
            "cx",
            "cnot",
            "cz",
            "ch",
            "cy",
            "cp",
            "crx",
            "cry",
            "crz",
            "cu",
            "cu1",
            "cu3",
        }

        if gate_name in {"ccx", "toffoli"} and len(qubit_indices) >= 3:
            return [qubit_indices[-1]], qubit_indices[:-1]
        if gate_name == "cswap" and len(qubit_indices) >= 3:
            return qubit_indices[1:], [qubit_indices[0]]
        if gate_name in controlled_names and len(qubit_indices) >= 2:
            return [qubit_indices[-1]], qubit_indices[:-1]

        return qubit_indices, []

    def _extract_index_list_with_context(self, node: ast.AST, loop_ctx: Dict[str, int]) -> List[int]:
        """Extract index list with loop context for variable resolution."""
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "range":
            return self._extract_range_indices(node)

        if isinstance(node, (ast.List, ast.Tuple)):
            out = []
            for elt in node.elts:
                idx = self._extract_single_index_with_context(elt, loop_ctx)
                if idx is not None:
                    out.append(idx)
            return out

        single = self._extract_single_index_with_context(node, loop_ctx)
        return [single] if single is not None else []

    def _extract_single_index_with_context(self, node: ast.AST, loop_ctx: Dict[str, int]) -> Optional[int]:
        """Extract single index with loop context for variable resolution."""
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return int(node.value)

        if isinstance(node, ast.Name):
            # First check loop context
            if node.id in loop_ctx:
                return loop_ctx[node.id]
            # Then check symbol table
            if node.id in self.symbol_table:
                return self.symbol_table[node.id]
            # Fallback for unresolved symbolic indices
            return 0

        if isinstance(node, ast.BinOp):
            value = self._eval_int_expr(node)
            return value if value is not None else 0

        if isinstance(node, ast.Subscript):
            return self._extract_single_index_with_context(node.slice, loop_ctx)

        return 0

    def extract_measurements(self) -> List[MeasurementNode]:
        measurements: List[MeasurementNode] = []
        if self.tree is None:
            return measurements

        for node in ast.walk(self.tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue

            owner = node.func.value
            if not isinstance(owner, ast.Name) or owner.id not in self.circuit_vars:
                continue

            method = node.func.attr
            if method == "measure_all":
                measurements.append(
                    MeasurementNode(
                        quantum_register="ALL",
                        classical_register="ALL",
                        qubit_indices=[],
                        classical_indices=[],
                        line_number=node.lineno,
                    )
                )
            elif method == "measure":
                q_idx = self._extract_index_list(node.args[0]) if node.args else []
                c_idx = self._extract_index_list(node.args[1]) if len(node.args) > 1 else []
                measurements.append(
                    MeasurementNode(
                        quantum_register="q",
                        classical_register="c",
                        qubit_indices=q_idx,
                        classical_indices=c_idx,
                        line_number=node.lineno,
                    )
                )

        return measurements

    def _extract_gate_qubits(self, gate_name: str, args: List[ast.AST]) -> (List[int], List[int]):
        n_params = self._GATE_PARAM_COUNTS.get(gate_name, 0)
        qubit_indices: List[int] = []
        for arg in args[n_params:]:
            qubit_indices.extend(self._extract_index_list(arg))

        controlled_names = {
            "cx",
            "cnot",
            "cz",
            "ch",
            "cy",
            "cp",
            "crx",
            "cry",
            "crz",
            "cu",
            "cu1",
            "cu3",
        }

        if gate_name in {"ccx", "toffoli"} and len(qubit_indices) >= 3:
            return [qubit_indices[-1]], qubit_indices[:-1]
        if gate_name == "cswap" and len(qubit_indices) >= 3:
            return qubit_indices[1:], [qubit_indices[0]]
        if gate_name in controlled_names and len(qubit_indices) >= 2:
            return [qubit_indices[-1]], qubit_indices[:-1]

        return qubit_indices, []

    def _extract_gate_params(self, gate_name: str, args: List[ast.AST]) -> List[float]:
        if gate_name not in {"rx", "ry", "rz", "cp", "crx", "cry", "crz", "cu", "cu1", "cu3"}:
            return []
        if not args:
            return []

        param_end = 1 if gate_name in {"rx", "ry", "rz", "cp", "crx", "cry", "crz", "cu1"} else min(4, len(args) - 1)
        out = []
        for p in args[:param_end]:
            if isinstance(p, ast.Constant) and isinstance(p.value, (int, float)):
                out.append(float(p.value))
        return out

    def _extract_index_list(self, node: ast.AST) -> List[int]:
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "range":
            return self._extract_range_indices(node)

        if isinstance(node, (ast.List, ast.Tuple)):
            out = []
            for elt in node.elts:
                idx = self._extract_single_index(elt)
                if idx is not None:
                    out.append(idx)
            return out

        single = self._extract_single_index(node)
        return [single] if single is not None else []

    def _extract_single_index(self, node: ast.AST) -> Optional[int]:
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return int(node.value)

        if isinstance(node, ast.Name):
            if node.id in self.symbol_table:
                return self.symbol_table[node.id]
            if node.id in self.loop_ranges:
                # When index comes from a loop variable, use first valid index.
                return 0
            # Fallback for unresolved symbolic indices (e.g., function args like n_count).
            return 0

        if isinstance(node, ast.BinOp):
            value = self._eval_int_expr(node)
            return value if value is not None else 0

        if isinstance(node, ast.Subscript):
            # q[2]
            idx_node = node.slice.value if isinstance(node.slice, ast.Index) else node.slice
            if isinstance(idx_node, ast.Constant) and isinstance(idx_node.value, int):
                return int(idx_node.value)
            if isinstance(idx_node, ast.Name):
                if idx_node.id in self.symbol_table:
                    return self.symbol_table[idx_node.id]
                if idx_node.id in self.loop_ranges:
                    return 0

        return None

    def _assign_target_name(self, targets: List[ast.expr]) -> Optional[str]:
        if not targets:
            return None
        target = targets[0]
        if isinstance(target, ast.Name):
            return target.id
        return None

    def _const_int(self, node: ast.AST) -> int:
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return int(node.value)
        return 0

    def _const_str(self, node: ast.AST) -> Optional[str]:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None
    
    def _infer_qubit_count_from_gates(self) -> int:
        """
        Infer qubit count from gate operations when register size is unknown.
        Returns the maximum qubit index + 1 found in gate operations.
        """
        if self.tree is None:
            return 0
        
        max_qubit_index = -1
        
        for node in ast.walk(self.tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            
            owner = node.func.value
            if not isinstance(owner, ast.Name):
                continue
            if owner.id not in self.circuit_vars:
                continue
            
            gate_name = node.func.attr.lower()
            if gate_name not in self.gate_mapping:
                continue
            
            # Extract qubit indices from gate arguments
            for arg in node.args:
                indices = self._extract_index_list(arg)
                if indices:
                    max_qubit_index = max(max_qubit_index, max(indices))
        
        return max_qubit_index + 1 if max_qubit_index >= 0 else 0

    def _build_symbol_table(self) -> None:
        """Collect simple integer assignments like n = 3 for expression resolution."""
        if self.tree is None or not isinstance(self.tree, ast.Module):
            return

        # Process in source order so dependent assignments (e.g., n = len(b)) resolve.
        for node in self.tree.body:
            if not isinstance(node, ast.Assign):
                continue
            if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                continue

            name = node.targets[0].id
            value = self._eval_static_value(node.value)
            if value is not None:
                self.symbol_table[name] = value

    def _collect_loop_ranges(self) -> None:
        """Collect for-loop bounds for patterns like for i in range(n)."""
        if self.tree is None:
            return

        for node in ast.walk(self.tree):
            if not isinstance(node, ast.For):
                continue
            if not isinstance(node.target, ast.Name):
                continue
            if not isinstance(node.iter, ast.Call):
                continue
            if not isinstance(node.iter.func, ast.Name) or node.iter.func.id != "range":
                continue

            values = self._extract_range_indices(node.iter)
            if values:
                self.loop_ranges[node.target.id] = len(values)

    def _extract_range_indices(self, node: ast.Call) -> List[int]:
        """Resolve Python range(...) calls with simple integer expressions."""
        args = node.args
        if len(args) == 1:
            start = 0
            stop = self._eval_int_expr(args[0])
            step = 1
        elif len(args) == 2:
            start = self._eval_int_expr(args[0])
            stop = self._eval_int_expr(args[1])
            step = 1
        elif len(args) >= 3:
            start = self._eval_int_expr(args[0])
            stop = self._eval_int_expr(args[1])
            step = self._eval_int_expr(args[2])
        else:
            return []

        if start is None or stop is None or step is None or step == 0:
            return []

        try:
            return list(range(start, stop, step))
        except Exception:
            return []

    def _eval_int_expr(self, node: ast.AST) -> Optional[int]:
        """Evaluate a small subset of integer expressions used in canonical code."""
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return int(node.value)

        if isinstance(node, ast.Name):
            value = self.symbol_table.get(node.id)
            return value if isinstance(value, int) else None

        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "len":
            if len(node.args) != 1:
                return None
            resolved = self._eval_static_value(node.args[0])
            if isinstance(resolved, (str, list, tuple, dict)):
                return len(resolved)
            return None

        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            value = self._eval_int_expr(node.operand)
            return -value if value is not None else None

        if isinstance(node, ast.BinOp):
            left = self._eval_int_expr(node.left)
            right = self._eval_int_expr(node.right)
            if left is None or right is None:
                return None

            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.FloorDiv):
                return left // right if right != 0 else None

        return None

    def _eval_static_value(self, node: ast.AST) -> Optional[Any]:
        """Evaluate basic literal/static values used by canonical examples."""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, str)):
                return node.value
            return None

        int_value = self._eval_int_expr(node)
        if int_value is not None:
            return int_value

        if isinstance(node, ast.Name):
            return self.symbol_table.get(node.id)

        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "len":
            if len(node.args) != 1:
                return None
            base = self._eval_static_value(node.args[0])
            if isinstance(base, (str, list, tuple, dict)):
                return len(base)

        return None
