from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Optional

try:
    # Try relative imports first (when used as a module)
    from ..schemas.decision_engine import (
        CodeAnalysisInput,
        DecisionEngineResponse,
        HealthCheckResponse
    )
    from ..services.decision_engine_service import DecisionEngineService
    from ..config import get_settings
except ImportError:
    # Fall back to absolute imports (when run as a script)
    from schemas.decision_engine import (
        CodeAnalysisInput,
        DecisionEngineResponse,
        HealthCheckResponse
    )
    from services.decision_engine_service import DecisionEngineService
    from config import get_settings

router = APIRouter(prefix="/decision-engine", tags=["Decision Engine"])

# Dependency to get service instance
def get_decision_service() -> DecisionEngineService:
    """Dependency to get decision engine service"""
    settings = get_settings()
    return DecisionEngineService(
        model_path=settings.MODEL_PATH,
        scaler_path=settings.SCALER_PATH
    )

@router.post("/predict", response_model=DecisionEngineResponse)
async def predict_hardware(
    input_data: CodeAnalysisInput,
    budget_limit_usd: Optional[float] = None,
    service: DecisionEngineService = Depends(get_decision_service)
):
    """
    Predict optimal hardware for given code analysis
    
    This endpoint receives code analysis results and returns a hardware recommendation
    using the trained machine learning model.
    
    - **problem_type**: Type of computational problem
    - **problem_size**: Size of the problem
    - **qubits_required**: Number of qubits needed (0 for classical)
    - **Other features**: Various quantum and classical metrics
    - **budget_limit_usd**: Optional budget constraint in USD
    
    Returns hardware recommendation with confidence scores and rationale.
    """
    response = service.predict(input_data, budget_limit_usd)
    
    if not response.success:
        raise HTTPException(status_code=500, detail=response.error)
    
    return response

@router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    service: DecisionEngineService = Depends(get_decision_service)
):
    """
    Check Decision Engine service health
    
    Returns information about model loading status and performance metrics.
    """
    health = service.health_check()
    
    return HealthCheckResponse(
        status="healthy" if health["model_loaded"] else "unhealthy",
        model_loaded=health["model_loaded"],
        model_type=health["model_type"],
        model_accuracy=health["model_accuracy"]
    )

@router.get("/model-info")
async def get_model_info(
    service: DecisionEngineService = Depends(get_decision_service)
) -> Dict:
    """
    Get detailed model information
    
    Returns feature columns, encoding mappings, and model metadata.
    """
    if not service.model_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_type": service.model_type,
        "model_accuracy": service.model_accuracy,
        "feature_columns": service.feature_columns,
        "problem_type_encoding": {k.value: v for k, v in service.problem_type_encoding.items()},
        "time_complexity_encoding": {k.value: v for k, v in service.time_complexity_encoding.items()}
    }