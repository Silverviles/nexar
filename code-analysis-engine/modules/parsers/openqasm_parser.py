"""OpenQASM parser using official Qiskit OpenQASM importers when available."""
import re
from typing import Any, Dict, List, Optional

from .base_parser import BaseParser
from models.unified_ast import (
    ClassicalRegisterNode,
    GateType,
    MeasurementNode,
    QuantumGateNode,
    QuantumRegisterNode,
)


class OpenQASMParser(BaseParser):
    """Parser for OpenQASM 2/3 programs."""

    def __init__(self):
        super().__init__()
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
            "cp": GateType.CP,
            "crx": GateType.CRX,
            "cry": GateType.CRY,
            "crz": GateType.CRZ,
            "barrier": GateType.BARRIER,
            "reset": GateType.RESET,
            "measure": GateType.MEASURE,
        }

    def parse(self, code: str) -> Dict[str, Any]:
        self.code = code
        self.lines = [line.strip() for line in code.splitlines() if line.strip()]

        registers = self.extract_registers()
        gates, measurements = self._extract_with_official_qiskit_parser(code)

        if not gates and not measurements:
            gates = self.extract_quantum_operations()
            measurements = self.extract_measurements()

        return {
            "imports": self.extract_imports(),
            "registers": registers,
            "gates": gates,
            "measurements": measurements,
            "functions": [],
            "metadata": {
                "lines_of_code": self.count_lines(code),
                "loop_count": self.count_loops(code),
                "conditional_count": self.count_conditionals(code),
                "nesting_depth": self.calculate_nesting_depth(code),
            },
        }

    def extract_imports(self) -> List[str]:
        return [line for line in self.lines if line.startswith("include")]

    def extract_registers(self) -> Dict[str, Any]:
        quantum_regs = []
        classical_regs = []

        qreg_pattern = r"qreg\s+(\w+)\[(\d+)\]"
        creg_pattern = r"creg\s+(\w+)\[(\d+)\]"
        q3_qubit_pattern = r"qubit\[(\d+)\]\s+(\w+)"
        q3_bit_pattern = r"bit\[(\d+)\]\s+(\w+)"

        for i, line in enumerate(self.lines):
            qreg_match = re.search(qreg_pattern, line)
            if qreg_match:
                quantum_regs.append(
                    QuantumRegisterNode(name=qreg_match.group(1), size=int(qreg_match.group(2)), line_number=i + 1)
                )

            creg_match = re.search(creg_pattern, line)
            if creg_match:
                classical_regs.append(
                    ClassicalRegisterNode(name=creg_match.group(1), size=int(creg_match.group(2)), line_number=i + 1)
                )

            q3_q_match = re.search(q3_qubit_pattern, line)
            if q3_q_match:
                quantum_regs.append(
                    QuantumRegisterNode(name=q3_q_match.group(2), size=int(q3_q_match.group(1)), line_number=i + 1)
                )

            q3_b_match = re.search(q3_bit_pattern, line)
            if q3_b_match:
                classical_regs.append(
                    ClassicalRegisterNode(name=q3_b_match.group(2), size=int(q3_b_match.group(1)), line_number=i + 1)
                )

        return {"quantum": quantum_regs, "classical": classical_regs}

    def extract_quantum_operations(self) -> List[QuantumGateNode]:
        gates = []
        gate_pattern = r"(\w+)(\([^)]*\))?\s+([\w\[\],\s]+);"

        for i, line in enumerate(self.lines):
            if line.startswith(("OPENQASM", "include", "qreg", "creg", "qubit", "bit", "measure", "barrier")):
                continue
            match = re.search(gate_pattern, line)
            if not match:
                continue

            gate_name = match.group(1).lower()
            if gate_name not in self.gate_mapping:
                continue

            qubits = self._extract_qubit_indices(match.group(3))
            controls, targets = self._split_controls_targets(gate_name, qubits)

            gates.append(
                QuantumGateNode(
                    gate_type=self.gate_mapping[gate_name],
                    qubits=targets,
                    control_qubits=controls,
                    is_controlled=bool(controls),
                    parameters=self._parse_parameters(match.group(2)),
                    line_number=i + 1,
                )
            )

        return gates

    def extract_measurements(self) -> List[MeasurementNode]:
        measurements = []
        pattern_pair = r"measure\s+(\w+)\[(\d+)\]\s*->\s*(\w+)\[(\d+)\]"
        pattern_bulk = r"measure\s+(\w+)\s*->\s*(\w+)"

        for i, line in enumerate(self.lines):
            pair_match = re.search(pattern_pair, line)
            if pair_match:
                measurements.append(
                    MeasurementNode(
                        quantum_register=pair_match.group(1),
                        classical_register=pair_match.group(3),
                        qubit_indices=[int(pair_match.group(2))],
                        classical_indices=[int(pair_match.group(4))],
                        line_number=i + 1,
                    )
                )
                continue

            bulk_match = re.search(pattern_bulk, line)
            if bulk_match:
                measurements.append(
                    MeasurementNode(
                        quantum_register=bulk_match.group(1),
                        classical_register=bulk_match.group(2),
                        qubit_indices=[],
                        classical_indices=[],
                        line_number=i + 1,
                    )
                )

        return measurements

    def _extract_with_official_qiskit_parser(self, code: str) -> (List[QuantumGateNode], List[MeasurementNode]):
        try:
            from qiskit import QuantumCircuit
        except Exception:
            return [], []

        qc = None
        version = self._detect_qasm_version(code)
        try:
            if version.startswith("3"):
                try:
                    from qiskit import qasm3

                    qc = qasm3.loads(code)
                except Exception:
                    qc = None
            else:
                qc = QuantumCircuit.from_qasm_str(code)
        except Exception:
            qc = None

        if qc is None:
            return [], []

        gates: List[QuantumGateNode] = []
        measurements: List[MeasurementNode] = []

        for instr in qc.data:
            name = instr.operation.name.lower()
            qargs = [qc.find_bit(bit).index for bit in instr.qubits]
            cargs = [qc.find_bit(bit).index for bit in instr.clbits]

            if name == "measure":
                measurements.append(
                    MeasurementNode(
                        quantum_register="q",
                        classical_register="c",
                        qubit_indices=qargs,
                        classical_indices=cargs,
                        line_number=None,
                    )
                )
                continue

            gate_type = self.gate_mapping.get(name, GateType.CUSTOM)
            controls, targets = self._split_controls_targets(name, qargs)

            params = []
            for p in instr.operation.params:
                if isinstance(p, (int, float)):
                    params.append(float(p))

            gates.append(
                QuantumGateNode(
                    gate_type=gate_type,
                    qubits=targets,
                    control_qubits=controls,
                    is_controlled=bool(controls),
                    parameters=params,
                    line_number=None,
                )
            )

        return gates, measurements

    def _detect_qasm_version(self, code: str) -> str:
        match = re.search(r"OPENQASM\s+(\d+(?:\.\d+)?)", code, flags=re.IGNORECASE)
        if not match:
            return "2.0"
        return match.group(1)

    def _extract_qubit_indices(self, qubits_str: str) -> List[int]:
        indices = []
        for value in re.findall(r"\[(\d+)\]", qubits_str):
            indices.append(int(value))
        return indices

    def _parse_parameters(self, param_str: Optional[str]) -> List[float]:
        if not param_str:
            return []
        inside = param_str.strip("()")
        inside = inside.replace("pi", "3.141592653589793")
        out = []
        for part in inside.split(","):
            expr = part.strip()
            try:
                out.append(float(eval(expr)))
            except Exception:
                continue
        return out

    def _split_controls_targets(self, gate_name: str, qubits: List[int]) -> (List[int], List[int]):
        if gate_name in {"cx", "cnot", "cz", "cp", "crx", "cry", "crz"} and len(qubits) >= 2:
            return qubits[:-1], [qubits[-1]]
        if gate_name in {"ccx", "toffoli"} and len(qubits) >= 3:
            return qubits[:-1], [qubits[-1]]
        return [], qubits
