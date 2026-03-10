"""Base parser abstractions and shared helpers."""
from abc import ABC, abstractmethod
import ast
import re
from typing import Any, Dict, List

from models.unified_ast import ASTNode, NodeType


class BaseParser(ABC):
    """Abstract base class for all language parsers."""

    def __init__(self):
        self.code = ""
        self.lines: List[str] = []

    @abstractmethod
    def parse(self, code: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def extract_imports(self) -> list:
        pass

    @abstractmethod
    def extract_quantum_operations(self) -> list:
        pass

    @abstractmethod
    def extract_registers(self) -> Dict[str, Any]:
        pass

    def count_lines(self, code: str) -> int:
        lines = [line.strip() for line in code.split("\n")]
        return len([line for line in lines if line and not line.startswith("#")])

    def extract_functions(self, code: str) -> List[ASTNode]:
        functions: List[ASTNode] = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(
                        ASTNode(
                            node_type=NodeType.FUNCTION,
                            name=node.name,
                            line_number=node.lineno,
                            children=[],
                            attributes={"args": [arg.arg for arg in node.args.args]},
                        )
                    )
        except Exception:
            pattern = r"(?:def|operation|function)\s+(\w+)\s*\("
            for match in re.finditer(pattern, code):
                functions.append(
                    ASTNode(
                        node_type=NodeType.FUNCTION,
                        name=match.group(1),
                        line_number=None,
                        children=[],
                        attributes={},
                    )
                )
        return functions

    def count_loops(self, code: str) -> int:
        loop_keywords = ["for", "while", "repeat", "loop"]
        count = 0
        for line in code.split("\n"):
            line_lower = line.strip().lower()
            if any(line_lower.startswith(kw) for kw in loop_keywords):
                count += 1
        return count

    def count_conditionals(self, code: str) -> int:
        conditional_keywords = ["if", "else", "elif", "switch", "case"]
        count = 0
        for line in code.split("\n"):
            line_lower = line.strip().lower()
            if any(line_lower.startswith(kw) for kw in conditional_keywords):
                count += 1
        return count

    def calculate_nesting_depth(self, code: str) -> int:
        max_depth = 0
        current_depth = 0
        for char in code:
            if char in "{[(":
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char in "})]":
                current_depth = max(0, current_depth - 1)

        for line in code.split("\n"):
            indent = len(line) - len(line.lstrip())
            depth = indent // 4
            max_depth = max(max_depth, depth)

        return max_depth

    def extract_python_control_flow_metadata(self, code: str) -> Dict[str, Any]:
        """Extract loops/conditionals and line-level loop multipliers from Python AST."""
        metadata: Dict[str, Any] = {
            "line_loop_multiplier": {},
            "loop_count": 0,
            "conditional_count": 0,
            "nesting_depth": 0,
            "control_flow_nesting_depth": 0,
            "structural_nesting_depth": 0,
        }

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return metadata

        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While, ast.AsyncFor)):
                metadata["loop_count"] += 1
            if isinstance(node, ast.If):
                metadata["conditional_count"] += 1

        # Control-flow depth ignores module/function/class wrappers.
        def visit_control_flow(nodes: List[ast.stmt], multiplier: int, depth: int) -> None:
            metadata["control_flow_nesting_depth"] = max(metadata["control_flow_nesting_depth"], depth)
            for stmt in nodes:
                line_no = getattr(stmt, "lineno", None)
                if line_no is not None:
                    metadata["line_loop_multiplier"][str(line_no)] = max(
                        multiplier,
                        metadata["line_loop_multiplier"].get(str(line_no), 1),
                    )

                if isinstance(stmt, (ast.For, ast.AsyncFor)):
                    loop_mult = self._infer_for_loop_iterations(stmt)
                    visit_control_flow(stmt.body, multiplier * loop_mult, depth + 1)
                    visit_control_flow(stmt.orelse, multiplier, depth)
                elif isinstance(stmt, ast.While):
                    visit_control_flow(stmt.body, multiplier, depth + 1)
                    visit_control_flow(stmt.orelse, multiplier, depth)
                elif isinstance(stmt, ast.If):
                    visit_control_flow(stmt.body, multiplier, depth + 1)
                    visit_control_flow(stmt.orelse, multiplier, depth)
                elif isinstance(stmt, ast.Try):
                    visit_control_flow(stmt.body, multiplier, depth + 1)
                    for handler in stmt.handlers:
                        visit_control_flow(handler.body, multiplier, depth + 1)
                    visit_control_flow(stmt.orelse, multiplier, depth)
                    visit_control_flow(stmt.finalbody, multiplier, depth)
                elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    # Function/class wrappers do not increase control-flow depth.
                    visit_control_flow(stmt.body, multiplier, depth)

        # Structural depth includes wrappers such as function/class definitions.
        def visit_structural(nodes: List[ast.stmt], depth: int) -> None:
            metadata["structural_nesting_depth"] = max(metadata["structural_nesting_depth"], depth)
            for stmt in nodes:
                if isinstance(stmt, (ast.For, ast.AsyncFor, ast.While, ast.If, ast.Try)):
                    visit_structural(getattr(stmt, "body", []), depth + 1)
                    visit_structural(getattr(stmt, "orelse", []), depth)
                    if isinstance(stmt, ast.Try):
                        for handler in stmt.handlers:
                            visit_structural(handler.body, depth + 1)
                        visit_structural(stmt.finalbody, depth)
                elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    visit_structural(stmt.body, depth + 1)

        visit_control_flow(tree.body, multiplier=1, depth=0)
        visit_structural(tree.body, depth=1)
        # Backward-compatible alias now points to control-flow depth.
        metadata["nesting_depth"] = metadata["control_flow_nesting_depth"]
        return metadata

    def _infer_for_loop_iterations(self, loop_node: ast.stmt) -> int:
        if not isinstance(loop_node, (ast.For, ast.AsyncFor)):
            return 1

        iter_node = loop_node.iter
        if (
            isinstance(iter_node, ast.Call)
            and isinstance(iter_node.func, ast.Name)
            and iter_node.func.id == "range"
        ):
            args = iter_node.args
            if len(args) == 1 and isinstance(args[0], ast.Constant) and isinstance(args[0].value, int):
                return max(args[0].value, 1)
            if (
                len(args) == 2
                and isinstance(args[0], ast.Constant)
                and isinstance(args[1], ast.Constant)
                and isinstance(args[0].value, int)
                and isinstance(args[1].value, int)
            ):
                return max(args[1].value - args[0].value, 1)
        return 1
