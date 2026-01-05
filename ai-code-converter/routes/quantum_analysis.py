"""
Quantum Pattern Analysis Router
"""
from fastapi import APIRouter, HTTPException
from typing import List

from models.quantum_analysis import (
    AnalysisRequest,
    AnalysisResponse,
    BatchAnalysisRequest,
    BatchAnalysisResponse,
    PatternsResponse,
    PatternDetection,
    QuantumSuitability,
    CodeMetrics,
    SuitabilityLevel
)
from services.quantum_pattern_recognizer import recognizer

router = APIRouter(
    prefix="/quantum",
    tags=["quantum-analysis"],
    responses={404: {"description": "Not found"}},
)


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "quantum-pattern-recognizer"
    }


@router.get("/patterns", response_model=PatternsResponse)
async def list_patterns():
    """List all detectable patterns."""
    patterns = []
    for pattern_name, info in recognizer.QUANTUM_MAPPINGS.items():
        patterns.append({
            "pattern": pattern_name,
            "quantum_algorithm": info['quantum_algo'],
            "expected_speedup": info['speedup'],
            "base_suitability": info['suitability_score']
        })
    
    return PatternsResponse(
        patterns=patterns,
        count=len(patterns)
    )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_code(request: AnalysisRequest):
    """
    Analyze Python code for quantum suitability.
    
    Request:
    - code: Python code to analyze
    - include_code: Whether to include original code in response (default: false)
    
    Returns:
    - Detected patterns with quantum mappings
    - Suitability score and level
    - Code metrics
    - Original code (only if include_code=true or suitability is high)
    """
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="No code provided")
    
    # Perform analysis
    result = recognizer.analyze(request.code)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    
    # Convert patterns to response format
    patterns = []
    for pattern in result.patterns:
        patterns.append(PatternDetection(
            pattern=pattern.name,
            confidence=pattern.confidence,
            quantum_algo=pattern.quantum_algo,
            speedup=pattern.speedup,
            suitability_score=pattern.suitability_score
        ))
    
    # Create suitability object
    suitability = QuantumSuitability(
        score=result.suitability_score,
        level=result.suitability_level,
        message=result.message
    )
    
    # Create metrics object
    metrics = CodeMetrics(**result.metrics)
    
    # Prepare response
    response = AnalysisResponse(
        success=True,
        patterns=patterns,
        quantum_suitability=suitability,
        metrics=metrics
    )
    
    # Add original code based on request or high suitability
    if request.include_code or result.suitability_level == SuitabilityLevel.HIGH:
        response.original_code = request.code
    
    return response


@router.post("/analyze/batch", response_model=BatchAnalysisResponse)
async def analyze_batch(request: BatchAnalysisRequest):
    """
    Analyze multiple code snippets in batch.
    
    Request:
    - codes: List of code items with id and code
    
    Returns:
    - List of analysis results for each code item
    """
    if not request.codes:
        raise HTTPException(status_code=400, detail="No codes provided")
    
    results = []
    for item in request.codes:
        code_id = item.id
        code = item.code
        
        if code.strip():
            analysis_result = recognizer.analyze(code)
            if analysis_result.success:
                patterns = []
                for pattern in analysis_result.patterns:
                    patterns.append({
                        "pattern": pattern.name,
                        "confidence": pattern.confidence,
                        "quantum_algo": pattern.quantum_algo,
                        "speedup": pattern.speedup,
                        "suitability_score": pattern.suitability_score
                    })
                
                result_data = {
                    "id": code_id,
                    "success": True,
                    "patterns": patterns,
                    "quantum_suitability": {
                        "score": analysis_result.suitability_score,
                        "level": analysis_result.suitability_level,
                        "message": analysis_result.message
                    },
                    "metrics": analysis_result.metrics
                }
            else:
                result_data = {
                    "id": code_id,
                    "success": False,
                    "error": analysis_result.error
                }
        else:
            result_data = {
                "id": code_id,
                "success": False,
                "error": "Empty code"
            }
        
        results.append(result_data)
    
    return BatchAnalysisResponse(
        success=True,
        results=results,
        total_analyzed=len(results)
    )


# Test endpoint for demonstration
@router.get("/test")
async def test_analysis():
    """Test endpoint with example code."""
    linear_search = """
def search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1
"""
    
    result = recognizer.analyze(linear_search)
    
    if result.success:
        return {
            "success": True,
            "suitability": {
                "score": result.suitability_score,
                "level": result.suitability_level,
                "message": result.message
            },
            "patterns_detected": len(result.patterns),
            "patterns": [p.name for p in result.patterns]
        }
    else:
        return {"success": False, "error": result.error}