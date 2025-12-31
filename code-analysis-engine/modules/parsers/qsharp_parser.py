"""
Python and Q# Parsers
"""
import re
import ast
from typing import Dict, Any, List
from .base_parser import BaseParser
from models.unified_ast import QuantumRegisterNode, QuantumGateNode, GateType, ASTNode, NodeType

class PythonParser(BaseParser):
    """Parser for plain Python code (non-quantum)"""
    
    def parse(self, code: str) -> Dict[str, Any]:
        """Parse Python code"""
        self.code = code
        self.lines = code.split('\n')
        
        return {
            'imports': self.extract_imports(),
            'registers': {'quantum': [], 'classical': []},
            'gates': [],
            'measurements': [],
            'functions': self.extract_functions(code),
            'metadata': {
                'lines_of_code': self.count_lines(code),
                'loop_count': self.count_loops(code),
                'conditional_count': self.count_conditionals(code),
                'nesting_depth': self.calculate_nesting_depth(code)
            }
        }
    
    def extract_imports(self) -> List[str]:
        """Extract Python imports"""
        imports = []
        for line in self.lines:
            if line.strip().startswith(('import ', 'from ')):
                imports.append(line.strip())
        return imports
    
    def extract_quantum_operations(self) -> List[QuantumGateNode]:
        """No quantum operations in plain Python"""
        return []
    
    def extract_registers(self) -> Dict[str, Any]:
        """No quantum registers in plain Python"""
        return {'quantum': [], 'classical': []}


class QSharpParser(BaseParser):
    """Parser for Q# code with support for parameterized and controlled gates."""
    
    def __init__(self):
        super().__init__()
        # Expanded gate mapping including measurement and basic gates
        self.gate_mapping = {
            'H': GateType.H,
            'X': GateType.X,
            'Y': GateType.Y,
            'Z': GateType.Z,
            'S': GateType.S,
            'T': GateType.T,
            'CNOT': GateType.CNOT,
            'CX': GateType.CX,
            'CZ': GateType.CZ,
            'SWAP': GateType.SWAP,
            'M': GateType.MEASURE,      # Q# alias for Measure on single qubit
            'Measure': GateType.MEASURE,
            'Reset': GateType.RESET
        }
    
    def parse(self, code: str) -> Dict[str, Any]:
        self.code = code
        self.lines = code.split('\n')
        
        return {
            'imports': self.extract_imports(),
            'registers': self.extract_registers(),
            'gates': self.extract_quantum_operations(),
            'measurements': [],  # Could populate from Measure ops if needed
            'functions': self.extract_qsharp_functions(),
            'metadata': {
                'lines_of_code': self.count_lines(code),
                'loop_count': self.count_loops(code),
                'conditional_count': self.count_conditionals(code),
                'nesting_depth': self.calculate_nesting_depth(code)
            }
        }
    
    def extract_imports(self) -> List[str]:
        """Extract Q# using/open statements"""
        imports = []
        for line in self.lines:
            stripped = line.strip()
            if stripped.startswith(('open ', 'using ')):
                imports.append(stripped)
        return imports
    
    def extract_registers(self) -> Dict[str, Any]:
        """Extract Q# qubit allocations (using statements)"""
        quantum_regs = []
        # Pattern: using (name = Qubit[n]) or using (name = Qubit[n]) {
        qubit_pattern = re.compile(r'using\s*\(\s*(\w+)\s*=\s*Qubit\[(\d+)\]\s*\)')
        
        for i, line in enumerate(self.lines):
            match = qubit_pattern.search(line)
            if match:
                name = match.group(1)
                size = int(match.group(2))
                quantum_regs.append(QuantumRegisterNode(
                    name=name, size=size, line_number=i+1
                ))
        
        return {'quantum': quantum_regs, 'classical': []}
    
    def extract_quantum_operations(self) -> List[QuantumGateNode]:
        """Extract Q# quantum operations, including gates, rotations, measure, controlled ops."""
        gates = []
        
        for i, line in enumerate(self.lines):
            line = line.strip().rstrip(';')
            
            # Skip empty or non-operations
            if not line or line.startswith('//') or line.startswith('using') or line.startswith('if ') or line.startswith('for '):
                continue

            # Handle controlled functors: (Controlled Gate)([controls], args)
            # e.g. (Controlled X)([q0], q1) or (Controlled R1)([c], (theta, q))
            if 'Controlled' in line:
                ctrl_match = re.search(
                    r'Controlled\s+(\w+)\s*\(\s*\[([^\]]*)\],\s*(.*)\)',
                    line
                )
                if ctrl_match:
                    base_gate = ctrl_match.group(1)

                    # count control qubits symbolically
                    ctrl_count = ctrl_match.group(2).count('qubits[')
                    control_qubits = [-1] * ctrl_count

                    args_str = ctrl_match.group(3).strip()
                    if args_str.startswith('('):
                        args_str = args_str.strip('()')

                    parts = [p.strip() for p in args_str.split(',')]

                    target_idx = -1
                    parameters = []

                    if len(parts) == 2:
                        param, target = parts
                        idx_match = re.search(r'\[(\w+)\]', target)
                        if idx_match and idx_match.group(1).isdigit():
                            target_idx = int(idx_match.group(1))
                        parameters.append(self._parse_parameter(param))

                    gate_type = self.gate_mapping.get(base_gate)
                    if base_gate == 'R1':
                        gate_type = GateType.RZ

                    if gate_type:
                        gates.append(QuantumGateNode(
                            gate_type=gate_type,
                            qubits=[target_idx],
                            parameters=parameters,
                            is_controlled=True,
                            control_qubits=control_qubits,
                            line_number=i + 1
                        ))
                continue
            
            # Simple gate invocation pattern: Gate(args)
            gate_match = re.match(r'(\w+)\s*\((.*)\)', line)
            if not gate_match:
                continue
            gate_name = gate_match.group(1)
            arg_list = gate_match.group(2)
            
            # Parameterized rotations: R(PauliX, angle, q) or R1(angle, q)
            if gate_name == 'R':
                # e.g. R(PauliZ, theta, q) -> map to RZ
                parts = [p.strip() for p in arg_list.split(',')]
                if len(parts) == 3:
                    pauli = parts[0]
                    angle_str = parts[1]
                    target_str = parts[2]
                    # Determine axis
                    axis = re.sub(r'Pauli', '', pauli)
                    target_idx = int(re.search(r'\[(\d+)\]', target_str).group(1))
                    angle = self._parse_parameter(parts[0])

                    gate_type = {
                        'X': GateType.RX,
                        'Y': GateType.RY,
                        'Z': GateType.RZ
                    }.get(axis, GateType.CUSTOM)
                    gates.append(QuantumGateNode(
                        gate_type=gate_type,
                        qubits=[target_idx],
                        parameters=[angle],
                        is_controlled=False,
                        control_qubits=[],
                        line_number=i+1
                    ))
                continue
            
            if gate_name == 'R1':
                # R1(angle, qubit)
                parts = [p.strip() for p in arg_list.split(',')]
                if len(parts) == 2:
                    angle = self._parse_parameter(parts[0])
                    target_str = parts[1]
                    target_idx = int(re.search(r'\[(\d+)\]', target_str).group(1))
                    gates.append(QuantumGateNode(
                        gate_type=GateType.RZ,  # treat R1 as RZ for parser purposes
                        qubits=[target_idx],
                        parameters=[angle],
                        is_controlled=False,
                        control_qubits=[],
                        line_number=i+1
                    ))
                continue
            
            # Map simple gates using gate_mapping
            if gate_name in self.gate_mapping:
                gate_type = self.gate_mapping[gate_name]
                # Split arguments (handles 1 or 2 qubits)
                args = [arg.strip() for arg in arg_list.split(',')]
                control_qubits = []
                target_qubits = []
                for arg in args:
                    if not arg: 
                        continue
                    # detect index inside brackets
                    idx_match = re.search(r'\[(\w+)\]', arg)
                    if idx_match:
                        idx = int(idx_match.group(1)) if idx_match.group(1).isdigit() else -1
                        if gate_type in {GateType.CNOT, GateType.CX, GateType.CZ}:
                            # Assume first arg is control
                            if not target_qubits:
                                control_qubits.append(idx)
                            else:
                                target_qubits.append(idx)
                        else:
                            target_qubits.append(idx)
                    else:
                        # If no brackets, assume single qubit variable (treat as 0 or skip)
                        pass
                is_ctrl = len(control_qubits) > 0
                # For 2-qubit gates not explicitly Controlled, first arg is control for CNOT/CZ
                if gate_type in {GateType.CNOT, GateType.CX, GateType.CZ} and len(target_qubits)==1 and len(control_qubits)==0:
                    control_qubits = [target_qubits[0]]
                    target_qubits = [target_qubits[1]] if len(target_qubits)>1 else []
                # Build gate node
                gates.append(QuantumGateNode(
                    gate_type=gate_type,
                    qubits=target_qubits if target_qubits else control_qubits,
                    parameters=[],
                    is_controlled=is_ctrl,
                    control_qubits=control_qubits,
                    line_number=i+1
                ))
        
        return gates
    
    def extract_qsharp_functions(self) -> List[ASTNode]:
        """Extract Q# operation/function definitions (with functor qualifiers)."""
        functions = []
        # Pattern matches operation or function with optional is Adj/Ctl
        pattern = re.compile(r'(?:operation|function)\s+(\w+)\s*\(.*?\)\s*:\s*\w+(?:\s*is\s*([^ {]+))?')
        for match in pattern.finditer(self.code):
            name = match.group(1)
            functors = match.group(2) or ""
            attrs = {"language": "qsharp"}
            # Detect functor support
            if 'Adj' in functors:
                attrs["adjointable"] = True
            if 'Ctl' in functors:
                attrs["controlledable"] = True
            functions.append(ASTNode(
                node_type=NodeType.FUNCTION,
                name=name,
                line_number=None,
                children=[],
                attributes=attrs
            ))
        return functions
    
    def _parse_parameter(self, param: str):
        try:
            return float(param)
        except Exception:
            return "symbolic"