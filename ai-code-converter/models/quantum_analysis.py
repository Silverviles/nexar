"""
Pydantic models for Quantum Pattern Analysis API
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum


class SuitabilityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PatternDetection(BaseModel):
    pattern: str
    confidence: float
    quantum_algo: str
    speedup: str
    suitability_score: float


class QuantumSuitability(BaseModel):
    score: float
    level: SuitabilityLevel
    message: str


class CodeMetrics(BaseModel):
    has_function: bool
    has_loop: bool
    has_condition: bool
    line_count: int
    function_count: int
    loop_count: int
    condition_count: int


class PatternInfo(BaseModel):
    pattern: str
    quantum_algorithm: str
    expected_speedup: str
    base_suitability: float


class AnalysisRequest(BaseModel):
    code: str
    include_code: Optional[bool] = False


class CodeItem(BaseModel):
    id: str
    code: str


class BatchAnalysisRequest(BaseModel):
    codes: List[CodeItem]


class AnalysisResponse(BaseModel):
    success: bool
    patterns: List[PatternDetection]
    quantum_suitability: QuantumSuitability
    metrics: CodeMetrics
    original_code: Optional[str] = None
    error: Optional[str] = None


class BatchAnalysisResponse(BaseModel):
    success: bool
    results: List[Dict[str, Any]]
    total_analyzed: int
    error: Optional[str] = None


class PatternsResponse(BaseModel):
    patterns: List[PatternInfo]
    count: int