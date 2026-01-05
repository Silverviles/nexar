from enum import Enum
from typing import Dict, List

class GateInfo:
    def __init__(self, name: str, description: str, qiskit_name: str):
        self.name = name
        self.description = description
        self.qiskit_name = qiskit_name

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "description": self.description,
            "qiskit_name": self.qiskit_name
        }

class BasisGates(Enum):
    CX = GateInfo("CNOT", "Controlled-NOT gate", "cx")
    CZ = GateInfo("CZ", "Controlled-Z gate", "cz")
    ID = GateInfo("Identity", "Identity gate (no-op)", "id")
    RZ = GateInfo("RZ", "Rotation around Z-axis", "rz")
    SX = GateInfo("SX", "Square root of X gate", "sx")
    X = GateInfo("X", "Pauli-X gate (NOT)", "x")
    Y = GateInfo("Y", "Pauli-Y gate", "y")
    Z = GateInfo("Z", "Pauli-Z gate", "z")
    H = GateInfo("H", "Hadamard gate", "h")
    S = GateInfo("S", "Phase gate", "s")
    T = GateInfo("T", "T gate", "t")
    ECR = GateInfo("ECR", "Echoed Cross Resonance", "ecr")

    @classmethod
    def get_info(cls, qiskit_name: str) -> Dict[str, str]:
        for gate in cls:
            if gate.value.qiskit_name == qiskit_name:
                return gate.value.to_dict()
        return {"name": qiskit_name.upper(), "description": "Unknown Gate", "qiskit_name": qiskit_name}

    @classmethod
    def all_gates(cls) -> List[Dict[str, str]]:
        return [gate.value.to_dict() for gate in cls]
