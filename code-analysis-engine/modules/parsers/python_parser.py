"""Plain Python parser (classical code path)."""
import ast
from typing import Any, Dict, List, Optional

from .base_parser import BaseParser
from models.unified_ast import QuantumGateNode


class PythonParser(BaseParser):
    """Parser for non-quantum Python code."""

    def __init__(self):
        super().__init__()
        self.tree: Optional[ast.AST] = None

    def parse(self, code: str) -> Dict[str, Any]:
        self.code = code
        self.lines = code.splitlines()

        try:
            self.tree = ast.parse(code)
        except SyntaxError:
            self.tree = None

        flow_meta = self.extract_python_control_flow_metadata(code)

        return {
            "imports": self.extract_imports(),
            "registers": {"quantum": [], "classical": []},
            "gates": [],
            "measurements": [],
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
            if stripped.startswith("import ") or stripped.startswith("from "):
                imports.append(stripped)
        return imports

    def extract_quantum_operations(self) -> List[QuantumGateNode]:
        return []

    def extract_registers(self) -> Dict[str, Any]:
        return {"quantum": [], "classical": []}
