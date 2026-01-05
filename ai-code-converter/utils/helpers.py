"""Helper functions for code analysis"""
import ast
from typing import Optional

def extract_logic_function(python_code: str) -> str:
    """
    Detect logic operations in Python code and return a minimal function.
    Only detects: XOR, AND, OR, NOT, NOR gates
    """
    try:
        tree = ast.parse(python_code)
        
        # Track which operations are found
        found_xor = False
        found_and = False
        found_or = False
        found_not = False
        found_nor = False
        
        class LogicFinder(ast.NodeVisitor):
            def visit_BinOp(self, node):
                nonlocal found_xor, found_and, found_or
                if isinstance(node.op, ast.BitXor):
                    found_xor = True
                elif isinstance(node.op, ast.BitAnd):
                    found_and = True
                elif isinstance(node.op, ast.BitOr):
                    found_or = True
                elif isinstance(node.op, ast.And):
                    found_and = True
                elif isinstance(node.op, ast.Or):
                    found_or = True
                self.generic_visit(node)
            
            def visit_UnaryOp(self, node):
                nonlocal found_not
                if isinstance(node.op, ast.Not) or isinstance(node.op, ast.Invert):
                    found_not = True
                self.generic_visit(node)
            
            def visit_Compare(self, node):
                nonlocal found_xor
                # Check for XOR pattern: a != b
                if len(node.ops) == 1 and isinstance(node.ops[0], ast.NotEq):
                    found_xor = True
                self.generic_visit(node)
            
            def visit_Call(self, node):
                nonlocal found_nor
                # Check for NOR pattern: not (a or b)
                if isinstance(node.func, ast.Name) and node.func.id == 'not':
                    for arg in node.args:
                        if isinstance(arg, ast.BoolOp) and isinstance(arg.op, ast.Or):
                            found_nor = True
                            found_not = True
                self.generic_visit(node)
            
            def visit_BoolOp(self, node):
                nonlocal found_nor
                # Check for NOR in context: not (a or b)
                if isinstance(node.op, ast.Or):
                    parent = getattr(node, 'parent', None)
                    while parent:
                        if isinstance(parent, ast.UnaryOp) and isinstance(parent.op, ast.Not):
                            found_nor = True
                            found_not = True
                            break
                        parent = getattr(parent, 'parent', None)
                self.generic_visit(node)
        
        # Add parent references to nodes for NOR detection
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        
        LogicFinder().visit(tree)
        
        # Check for NOR patterns in string
        if not found_nor:
            python_lower = python_code.lower()
            nor_patterns = [
                'not (a or b)', 'not (a | b)', 'not(a or b)', 'not(a | b)',
                'not (b or a)', 'not (b | a)', 'not (x or y)', 'not (x | y)'
            ]
            for pattern in nor_patterns:
                if pattern in python_lower:
                    found_nor = True
                    found_not = True
                    break
        
        # Determine which gate function to return
        if found_nor:
            return "def nor_gate(a, b):\n    return not (a or b)\n"
        elif found_xor:
            return "def xor_gate(a, b):\n    return a ^ b\n"
        elif found_and:
            return "def and_gate(a, b):\n    return a & b\n"
        elif found_or:
            return "def or_gate(a, b):\n    return a | b\n"
        elif found_not:
            # Extract variable name if possible
            lines = python_code.strip().split('\n')
            for line in lines:
                if '=' in line and ('not' in line.lower() or '~' in line):
                    parts = line.split('=')
                    if len(parts) > 1:
                        var_name = parts[0].strip()
                        # Clean up variable name
                        var_name = ''.join(c for c in var_name if c.isalnum() or c == '_')
                        return f"def not_gate({var_name}):\n    return not {var_name}\n"
            return "def not_gate(bit):\n    return not bit\n"
        else:
            # No recognizable logic pattern found
            return python_code
            
    except Exception as e:
        print(f"Failed to extract logic function: {e}")
        return python_code  # fallback to original