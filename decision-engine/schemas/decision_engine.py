from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum

class HardwareType(str, Enum):
    """Hardware types"""
    QUANTUM = "Quantum"
    CLASSICAL = "Classical"
    HYBRID = "Hybrid"

class ProblemType(str, Enum):
    """Problem types"""
    FACTORIZATION = "factorization"
    SEARCH = "search"
    SIMULATION = "simulation"
    OPTIMIZATION = "optimization"
    SORTING = "sorting"
    DYNAMIC_PROGRAMMING = "dynamic_programming"
    MATRIX_OPS = "matrix_ops"
    RANDOM_CIRCUIT = "random_circuit"

class TimeComplexity(str, Enum):
    """Time complexity types"""
    EXPONENTIAL = "exponential"
    POLYNOMIAL = "polynomial"
    QUADRATIC_SPEEDUP = "quadratic_speedup"
    POLYNOMIAL_SPEEDUP = "polynomial_speedup"
    NLOGN = "nlogn"

class CodeAnalysisInput(BaseModel):
    """Input from Code Analysis Engine"""
    problem_type: ProblemType = Field(..., description="Type of computational problem")
    problem_size: int = Field(..., ge=1, description="Size of the problem (e.g., number of elements)")
    qubits_required: int = Field(..., ge=0, description="Number of qubits needed (0 for classical)")
    circuit_depth: int = Field(..., ge=0, description="Depth of quantum circuit (0 for classical)")
    gate_count: int = Field(..., ge=0, description="Total number of gates (0 for classical)")
    cx_gate_ratio: float = Field(..., ge=0.0, le=1.0, description="Ratio of entangling gates")
    superposition_score: float = Field(..., ge=0.0, le=1.0, description="Superposition potential score")
    entanglement_score: float = Field(..., ge=0.0, le=1.0, description="Entanglement potential score")
    time_complexity: TimeComplexity = Field(..., description="Algorithm time complexity")
    memory_requirement_mb: float = Field(..., ge=0, description="Memory requirement in MB")

    class Config:
        json_schema_extra = {
            "example": {
                "problem_type": "optimization",
                "problem_size": 500,
                "qubits_required": 12,
                "circuit_depth": 150,
                "gate_count": 500,
                "cx_gate_ratio": 0.33,
                "superposition_score": 0.75,
                "entanglement_score": 0.70,
                "time_complexity": "polynomial_speedup",
                "memory_requirement_mb": 200.0
            }
        }

class HardwareRecommendation(BaseModel):
    """Hardware recommendation output"""
    recommended_hardware: HardwareType = Field(..., description="Recommended hardware type")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")
    quantum_probability: float = Field(..., ge=0.0, le=1.0, description="Probability of quantum being optimal")
    classical_probability: float = Field(..., ge=0.0, le=1.0, description="Probability of classical being optimal")
    rationale: str = Field(..., description="Explanation for the recommendation")

class DecisionEngineResponse(BaseModel):
    """Complete decision engine response"""
    success: bool = Field(..., description="Whether the prediction was successful")
    recommendation: Optional[HardwareRecommendation] = Field(default=None, description="Hardware recommendation")
    alternatives: Optional[list[dict]] = Field(default=None, description="Alternative options with trade-offs")
    estimated_execution_time_ms: Optional[float] = Field(default=None, description="Estimated execution time")
    estimated_cost_usd: Optional[float] = Field(default=None, description="Estimated cost in USD")
    error: Optional[str] = Field(default=None, description="Error message if prediction failed")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "recommendation": {
                    "recommended_hardware": "Quantum",
                    "confidence": 0.87,
                    "quantum_probability": 0.87,
                    "classical_probability": 0.13,
                    "rationale": "Problem exhibits strong quantum advantage with high superposition and entanglement scores"
                },
                "alternatives": [
                    {"hardware": "Classical", "confidence": 0.13, "trade_off": "Lower cost but slower execution"}
                ],
                "estimated_execution_time_ms": 1500.0,
                "estimated_cost_usd": 0.25,
                "error": None
            }
        }

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether ML model is loaded")
    model_type: Optional[str] = Field(None, description="Type of ML model")
    model_accuracy: Optional[float] = Field(None, description="Model test accuracy")