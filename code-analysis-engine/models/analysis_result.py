"""
Analysis Result Models
Output format for Decision Engine
"""
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, Dict, Any, List

class ProblemType(str, Enum):
    """Type of computational problem"""
    SEARCH = "search"
    OPTIMIZATION = "optimization"
    SIMULATION = "simulation"
    MACHINE_LEARNING = "machine_learning"
    FACTORIZATION = "factorization"
    CRYPTOGRAPHY = "cryptography"
    SAMPLING = "sampling"
    ORACLE_IDENTIFICATION = "oracle_identification"
    PROPERTY_TESTING = "property_testing"
    HIDDEN_STRUCTURE = "hidden_structure"
    CLASSICAL = "classical"
    UNKNOWN = "unknown"

class TimeComplexity(str, Enum):
    """Algorithm time complexity"""
    CONSTANT = "O(1)"
    LOGARITHMIC = "O(log n)"
    LINEAR = "O(n)"
    LINEARITHMIC = "O(n log n)"
    QUADRATIC = "O(n^2)"
    CUBIC = "O(n^3)"
    EXPONENTIAL = "O(2^n)"
    FACTORIAL = "O(n!)"
    POLYNOMIAL = "O(n^k)"
    QUANTUM_ADVANTAGE = "O(sqrt(n))"  # e.g., Grover
    UNKNOWN = "unknown"

class ClassicalComplexity(BaseModel):
    """Classical code complexity metrics"""
    cyclomatic_complexity: int = Field(..., description="Total McCabe complexity across analyzed functions")
    cyclomatic_complexity_max: int = Field(default=0, description="Maximum per-function McCabe complexity")
    cognitive_complexity: int = Field(default=0, description="Cognitive complexity")
    time_complexity: TimeComplexity = Field(..., description="Estimated time complexity")
    space_complexity: str = Field(default="O(1)", description="Space complexity")
    loop_count: int = Field(default=0, description="Number of loops")
    conditional_count: int = Field(default=0, description="Number of conditionals")
    function_count: int = Field(default=0, description="Number of functions")
    max_nesting_depth: int = Field(default=0, description="Maximum control-flow nesting depth (backward-compatible alias)")
    control_flow_nesting_depth: int = Field(default=0, description="Maximum control-flow nesting depth")
    structural_nesting_depth: int = Field(default=0, description="Maximum structural nesting depth (includes functions/classes)")
    lines_of_code: int = Field(default=0, description="Total lines of code")

class QuantumComplexity(BaseModel):
    """Quantum-specific complexity metrics"""
    qubits_required: int = Field(..., ge=0, description="Number of qubits needed")
    circuit_depth: int = Field(..., ge=0, description="Depth of quantum circuit")
    gate_count: int = Field(..., ge=0, description="Total number of gates")
    single_qubit_gates: int = Field(default=0, description="Single-qubit gate count")
    two_qubit_gates: int = Field(default=0, description="Two-qubit gate count")
    cx_gate_count: int = Field(default=0, description="CNOT/CX gate count")
    cx_gate_ratio: float = Field(..., ge=0.0, le=1.0, description="Ratio of entangling gates")
    measurement_count: int = Field(default=0, description="Number of measurements")
    
    # Quantum characteristics
    superposition_score: float = Field(..., ge=0.0, le=1.0, description="Superposition potential")
    entanglement_score: float = Field(..., ge=0.0, le=1.0, description="Entanglement potential")
    has_superposition: bool = Field(default=False, description="Uses superposition")
    has_entanglement: bool = Field(default=False, description="Uses entanglement")
    
    # Resource estimation
    logical_circuit_volume: Optional[float] = Field(default=None, description="Estimated logical_circuit volume")
    estimated_logical_runtime_ms: Optional[float] = Field(default=None, description="Estimated runtime")

class ASTNode(BaseModel):
    """AST Node for tree structure visualization"""
    type: str = Field(..., description="Node type (function, loop, conditional, gate, register, etc.)")
    name: Optional[str] = Field(default=None, description="Node name")
    line_number: Optional[int] = Field(default=None, description="Line number in source")
    complexity_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Complexity score")
    children: List["ASTNode"] = Field(default_factory=list, description="Child nodes")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional attributes")

class OptimizationSuggestion(BaseModel):
    """Optimization suggestion for code improvement"""
    category: str = Field(..., description="Category (e.g., 'performance', 'resources', 'structure')")
    severity: str = Field(..., description="Severity level (low, medium, high)")
    description: str = Field(..., description="Human-readable suggestion")
    expected_improvement: str = Field(..., description="Expected impact/improvement")
    estimated_savings: Optional[Dict[str, Any]] = Field(default=None, description="Estimated resource savings")

class CodeQualityMetrics(BaseModel):
    """Code quality assessment"""
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall quality score 0-100")
    maintainability_score: float = Field(..., ge=0.0, le=100.0, description="Maintainability score")
    performance_score: float = Field(..., ge=0.0, le=100.0, description="Performance efficiency score")
    resource_efficiency_score: float = Field(..., ge=0.0, le=100.0, description="Resource usage efficiency")
    code_complexity_rating: str = Field(..., description="Low/Medium/High/Very High")

class CodeAnalysisResult(BaseModel):
    """
    Complete code analysis result
    Output format for Decision Engine
    """
    # Language detection
    detected_language: str = Field(..., description="Detected programming language")
    language_confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    
    # Problem classification
    problem_type: ProblemType = Field(..., description="Type of computational problem")
    problem_size: int = Field(..., ge=1, description="Size of the problem")
    
    # Complexity metrics
    classical_metrics: Optional[ClassicalComplexity] = None
    quantum_metrics: Optional[QuantumComplexity] = None
    
    # Decision engine requirements (combined)
    qubits_required: int = Field(..., ge=0, description="Number of qubits (0 for classical)")
    circuit_depth: int = Field(..., ge=0, description="Circuit depth (0 for classical)")
    gate_count: int = Field(..., ge=0, description="Total gates (0 for classical)")
    cx_gate_ratio: float = Field(..., ge=0.0, le=1.0, description="Entangling gate ratio")
    superposition_score: float = Field(..., ge=0.0, le=1.0, description="Superposition score")
    entanglement_score: float = Field(..., ge=0.0, le=1.0, description="Entanglement score")
    time_complexity: TimeComplexity = Field(..., description="Algorithm time complexity")
    memory_requirement_mb: float = Field(..., ge=0, description="Memory requirement in MB")
    
    # Additional metadata
    is_quantum: bool = Field(default=False, description="Is quantum code")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall confidence")
    analysis_notes: str = Field(default="", description="Additional notes")
    
    # Algorithm detection (will be added later)
    detected_algorithms: list = Field(default_factory=list, description="Detected quantum algorithms")
    algorithm_detection_source: Optional[str] = None
    language_detection_method: str = Field(default="fallback", description="Language detection method: 'ml', 'fallback', or 'error'")
    
    # UI Enhancement Fields (optional)
    ast_structure: Optional[ASTNode] = Field(default=None, description="Abstract Syntax Tree for visualization")
    code_quality_metrics: Optional[CodeQualityMetrics] = Field(default=None, description="Code quality assessment")
    optimization_suggestions: List[OptimizationSuggestion] = Field(default_factory=list, description="Recommended optimizations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detected_language": "qiskit",
                "language_confidence": 0.95,
                "problem_type": "search",
                "problem_size": 4,
                "qubits_required": 4,
                "circuit_depth": 12,
                "gate_count": 15,
                "cx_gate_ratio": 0.33,
                "superposition_score": 1.0,
                "entanglement_score": 0.75,
                "time_complexity": "O(sqrt(n))",
                "memory_requirement_mb": 0.5,
                "is_quantum": True,
                "confidence_score": 0.9
            }
        }