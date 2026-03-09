"""Q# parser for operation-level semantic extraction."""
import re
from typing import Any, Dict, List

from .base_parser import BaseParser
from models.unified_ast import ASTNode, GateType, MeasurementNode, NodeType, QuantumGateNode, QuantumRegisterNode


class QSharpParser(BaseParser):
    """Parser for Q# source files."""

    def __init__(self):
        super().__init__()
        self.gate_mapping = {
            "H": GateType.H,
            "X": GateType.X,
            "Y": GateType.Y,
            "Z": GateType.Z,
            "S": GateType.S,
            "T": GateType.T,
            "R": GateType.CUSTOM,
            "Rx": GateType.RX,
            "Ry": GateType.RY,
            "Rz": GateType.RZ,
            "CNOT": GateType.CNOT,
            "CX": GateType.CX,
            "CZ": GateType.CZ,
            "SWAP": GateType.SWAP,
            "CCNOT": GateType.TOFFOLI,
            "Toffoli": GateType.TOFFOLI,
            "Reset": GateType.RESET,
            "M": GateType.MEASURE,
            "Measure": GateType.MEASURE,
            "MResetZ": GateType.MEASURE,
        }

    def parse(self, code: str) -> Dict[str, Any]:
        self.code = code
        self.lines = code.splitlines()

        return {
            "imports": self.extract_imports(),
            "registers": self.extract_registers(),
            "gates": self.extract_quantum_operations(),
            "measurements": self.extract_measurements(),
            "functions": self.extract_qsharp_functions(),
            "metadata": {
                "lines_of_code": self.count_lines(code),
                "loop_count": self._count_qsharp_loops(),
                "conditional_count": self._count_qsharp_conditionals(),
                "nesting_depth": self.calculate_nesting_depth(code),
            },
        }

    def extract_imports(self) -> List[str]:
        imports = []
        for line in self.lines:
            stripped = line.strip()
            if stripped.startswith("open ") or stripped.startswith("import "):
                imports.append(stripped)
        return imports

    def extract_registers(self) -> Dict[str, Any]:
        quantum_regs = []

        array_pattern = r"\buse\s+(\w+)\s*=\s*Qubit\[(\d+)\]"
        single_pattern = r"\buse\s+(\w+)\s*=\s*Qubit\s*\(\s*\)"

        for i, line in enumerate(self.lines):
            if array_match := re.search(array_pattern, line):
                quantum_regs.append(
                    QuantumRegisterNode(
                        name=array_match.group(1),
                        size=int(array_match.group(2)),
                        line_number=i + 1,
                    )
                )
            elif single_match := re.search(single_pattern, line):
                quantum_regs.append(
                    QuantumRegisterNode(name=single_match.group(1), size=1, line_number=i + 1)
                )

        if not quantum_regs:
            quantum_regs.append(QuantumRegisterNode(name="qubits", size=0, line_number=None))

        return {"quantum": quantum_regs, "classical": []}

    def extract_quantum_operations(self) -> List[QuantumGateNode]:
        gates = []

        # Matches forms like H(q[0]); CNOT(q[0], q[1]); Reset(q);
        gate_call = re.compile(r"\b([A-Za-z][A-Za-z0-9_]*)\s*\(([^)]*)\)\s*;")

        for i, line in enumerate(self.lines):
            for match in gate_call.finditer(line):
                gate_name = match.group(1)
                if gate_name not in self.gate_mapping:
                    continue

                gate_type = self.gate_mapping[gate_name]
                if gate_type == GateType.MEASURE:
                    continue

                args = [a.strip() for a in match.group(2).split(",") if a.strip()]
                qubits = [idx for idx in [self._extract_qubit_index(a) for a in args] if idx is not None]

                controls = []
                targets = qubits
                if gate_name in {"CNOT", "CX", "CZ"} and len(qubits) >= 2:
                    controls = [qubits[0]]
                    targets = [qubits[-1]]
                elif gate_name in {"CCNOT", "Toffoli"} and len(qubits) >= 3:
                    controls = qubits[:-1]
                    targets = [qubits[-1]]

                gates.append(
                    QuantumGateNode(
                        gate_type=gate_type,
                        qubits=targets,
                        control_qubits=controls,
                        is_controlled=bool(controls),
                        line_number=i + 1,
                    )
                )

        return gates

    def extract_measurements(self) -> List[MeasurementNode]:
        measurements = []
        # Regular measurement calls: M, Measure, MResetZ
        measure_call = re.compile(r"\b(M|Measure|MResetZ)\s*\(([^)]*)\)")
        # ForEach measurement pattern: ForEach(MResetZ, qubits) or ForEach(M, qubits)
        foreach_measure = re.compile(r"\bForEach\s*\(\s*(M|MResetZ|Measure)\s*,\s*([^)]+)\)")

        for i, line in enumerate(self.lines):
            # Check regular measurements
            for match in measure_call.finditer(line):
                args = [a.strip() for a in match.group(2).split(",") if a.strip()]
                q_idxs = [idx for idx in [self._extract_qubit_index(a) for a in args] if idx is not None]
                measurements.append(
                    MeasurementNode(
                        quantum_register="qubits",
                        classical_register="results",
                        qubit_indices=q_idxs,
                        classical_indices=list(range(len(q_idxs))),
                        line_number=i + 1,
                    )
                )
            
            # Check ForEach measurements
            for match in foreach_measure.finditer(line):
                qubit_arg = match.group(2).strip()
                # ForEach measures all qubits in the register
                measurements.append(
                    MeasurementNode(
                        quantum_register=qubit_arg,
                        classical_register="results",
                        qubit_indices=[],  # Measures all qubits in register
                        classical_indices=[],
                        line_number=i + 1,
                    )
                )

        return measurements

    def extract_qsharp_functions(self) -> List[ASTNode]:
        functions = []
        pattern = re.compile(r"\b(operation|function)\s+(\w+)\s*\(")

        for i, line in enumerate(self.lines):
            match = pattern.search(line)
            if not match:
                continue
            functions.append(
                ASTNode(
                    node_type=NodeType.FUNCTION,
                    name=match.group(2),
                    line_number=i + 1,
                    children=[],
                    attributes={"language": "qsharp", "kind": match.group(1)},
                )
            )

        return functions

    def _extract_qubit_index(self, arg: str):
        # q[2]
        idx_match = re.search(r"\[(\d+)\]", arg)
        if idx_match:
            return int(idx_match.group(1))

        # For single named qubits, keep deterministic placeholder 0.
        if re.match(r"^[A-Za-z_]\w*$", arg):
            return 0

        return None

    def _count_qsharp_loops(self) -> int:
        pattern = re.compile(r"^\s*(for|while|repeat)\b", flags=re.IGNORECASE)
        return sum(1 for line in self.lines if pattern.search(line))

    def _count_qsharp_conditionals(self) -> int:
        pattern = re.compile(r"^\s*(if|elif|else)\b", flags=re.IGNORECASE)
        return sum(1 for line in self.lines if pattern.search(line))
