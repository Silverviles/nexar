"""
AST Builder - Constructs unified AST from parsed code
"""
import logging
from typing import Dict, Any
from models.unified_ast import UnifiedAST
from modules.canonical_ir_builder import CanonicalIRBuilder
from modules.language_detector import SupportedLanguage
from modules.parsers import (
    QiskitParser, CirqParser, OpenQASMParser,
    PythonParser, QSharpParser
)

logger = logging.getLogger(__name__)

class ASTBuilder:
    """Builds unified AST from parsed code"""
    
    def __init__(self):
        self.ir_builder = CanonicalIRBuilder()
        self.parsers = {
            SupportedLanguage.QISKIT: QiskitParser(),
            SupportedLanguage.CIRQ: CirqParser(),
            SupportedLanguage.OPENQASM: OpenQASMParser(),
            SupportedLanguage.PYTHON: PythonParser(),
            SupportedLanguage.QSHARP: QSharpParser()
        }
    
    def build(self, code: str, language: SupportedLanguage) -> UnifiedAST:
        """
        Build unified AST from source code
        
        Args:
            code: Source code string
            language: Detected programming language
            
        Returns:
            UnifiedAST object
        """
        if language not in self.parsers:
            logger.error("Unsupported language for AST building: %s", language)
            raise ValueError(f"Unsupported language: {language}")
        
        # Parse code with appropriate parser
        parser = self.parsers[language]
        parsed_data = parser.parse(code)
        
        # Extract register information
        quantum_regs = parsed_data['registers'].get('quantum', [])
        classical_regs = parsed_data['registers'].get('classical', [])
        
        # Calculate total qubits and bits
        total_qubits = sum(reg.size for reg in quantum_regs)
        total_bits = sum(reg.size for reg in classical_regs)
        
        # Extract gates and measurements
        gates = parsed_data.get('gates', [])
        measurements = parsed_data.get('measurements', [])
        
        # Build unified AST
        unified_ast = UnifiedAST(
            source_language=language.value,
            quantum_registers=quantum_regs,
            classical_registers=classical_regs,
            gates=gates,
            measurements=measurements,
            imports=parsed_data.get('imports', []),
            functions=parsed_data.get('functions', []),
            total_qubits=total_qubits,
            total_classical_bits=total_bits,
            total_gates=len(gates)
        )
        
        logger.info(
            "Built unified AST for %s: %d qubits, %d gates, %d measurements",
            language.value, total_qubits, len(gates), len(measurements),
        )

        # Attach canonical IR so all downstream analyzers share a single semantic source.
        metadata = self.get_metadata(parsed_data)
        unified_ast.canonical_ir = self.ir_builder.build(unified_ast, metadata)
        
        return unified_ast
    
    def to_ir(self, unified_ast: UnifiedAST) -> Dict[str, Any]:
        """Serialize a built UnifiedAST into canonical IR format."""
        return unified_ast.to_ir()
    
    def get_metadata(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from parsed data"""
        metadata = parsed_data.get('metadata', {})
        return {
            'lines_of_code': metadata.get('lines_of_code', 0),
            'loop_count': metadata.get('loop_count', 0),
            'conditional_count': metadata.get('conditional_count', 0),
            'nesting_depth': metadata.get('nesting_depth', 0),
            'control_flow_nesting_depth': metadata.get('control_flow_nesting_depth', metadata.get('nesting_depth', 0)),
            'structural_nesting_depth': metadata.get('structural_nesting_depth', metadata.get('nesting_depth', 0)),
            'line_loop_multiplier': metadata.get('line_loop_multiplier', {}),
            'function_count': len(parsed_data.get('functions', []))
        }