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

        try:
            self.tree = ast.parse(code)
        except SyntaxError:
            self.tree = None

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
                size = self._const_int(node.value.args[0]) if node.value.args else 0
                reg_name = self._const_str(node.value.args[1]) if len(node.value.args) > 1 else target_name
                quantum_regs.append(
                    QuantumRegisterNode(name=reg_name or target_name, size=size, line_number=node.lineno)
                )
                self.register_sizes[target_name] = size

            elif ctor_name == "ClassicalRegister":
                size = self._const_int(node.value.args[0]) if node.value.args else 0
                reg_name = self._const_str(node.value.args[1]) if len(node.value.args) > 1 else target_name
                classical_regs.append(
                    ClassicalRegisterNode(name=reg_name or target_name, size=size, line_number=node.lineno)
                )
                self.register_sizes[target_name] = size

            elif ctor_name == "QuantumCircuit":
                self.circuit_vars.add(target_name)
                q_count = 0
                c_count = 0
                if len(node.value.args) >= 1 and isinstance(node.value.args[0], ast.Constant):
                    if isinstance(node.value.args[0].value, int):
                        q_count = node.value.args[0].value
                if len(node.value.args) >= 2 and isinstance(node.value.args[1], ast.Constant):
                    if isinstance(node.value.args[1].value, int):
                        c_count = node.value.args[1].value

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

        for node in ast.walk(self.tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue

            owner = node.func.value
            if not isinstance(owner, ast.Name):
                continue
            if owner.id not in self.circuit_vars:
                continue

            gate_name = node.func.attr.lower()
            if gate_name not in self.gate_mapping or gate_name in {"measure", "measure_all"}:
                continue

            gate_type = self.gate_mapping[gate_name]
            qubits, controls = self._extract_gate_qubits(gate_name, node.args)
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

        return gates

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
        qubit_indices = [idx for idx in [self._extract_single_index(a) for a in args] if idx is not None]

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

        if isinstance(node, ast.Subscript):
            # q[2]
            idx_node = node.slice.value if isinstance(node.slice, ast.Index) else node.slice
            if isinstance(idx_node, ast.Constant) and isinstance(idx_node.value, int):
                return int(idx_node.value)

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
