import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Optional, Any
import logging
import json

try:
    from ..schemas.decision_engine import (
        CodeAnalysisInput,
        HardwareRecommendation,
        DecisionEngineResponse,
        HardwareType,
        ProblemType,
        TimeComplexity
    )
except ImportError:
    from schemas.decision_engine import (
        CodeAnalysisInput,
        HardwareRecommendation,
        DecisionEngineResponse,
        HardwareType,
        ProblemType,
        TimeComplexity
    )

logger = logging.getLogger(__name__)

class DecisionEngineService:
    """Service for ML-based hardware recommendation"""
    
    def __init__(self, model_path: str, scaler_path: str):
        """
        Initialize the decision engine service
        
        Args:
            model_path: Path to the trained model pickle file
            scaler_path: Path to the feature scaler pickle file
        """
        self.model: Optional[Any] = None
        self.scaler: Optional[Any] = None
        self.model_loaded: bool = False
        self.model_type: Optional[str] = None
        self.model_accuracy: Optional[float] = None
        
        # Feature column order (must match training!)
        self.feature_columns = [
            'problem_size',
            'qubits_required',
            'circuit_depth',
            'gate_count',
            'cx_gate_ratio',
            'superposition_score',
            'entanglement_score',
            'memory_requirement_mb',
            'problem_type_encoded',
            'time_complexity_encoded'
        ]
        
        # CORRECTED: These match LabelEncoder's alphabetical ordering
        # Based on sorted order of your problem types
        self.problem_type_encoding = {
            ProblemType.DYNAMIC_PROGRAMMING: 0,  # alphabetically first
            ProblemType.FACTORIZATION: 1,
            ProblemType.MATRIX_OPS: 2,
            ProblemType.OPTIMIZATION: 3,
            ProblemType.RANDOM_CIRCUIT: 4,
            ProblemType.SEARCH: 5,
            ProblemType.SIMULATION: 6,
            ProblemType.SORTING: 7               # alphabetically last
        }
        
        # CORRECTED: These match LabelEncoder's alphabetical ordering
        self.time_complexity_encoding = {
            TimeComplexity.EXPONENTIAL: 0,       # alphabetically first
            TimeComplexity.NLOGN: 1,
            TimeComplexity.POLYNOMIAL: 2,
            TimeComplexity.POLYNOMIAL_SPEEDUP: 3,
            TimeComplexity.QUADRATIC_SPEEDUP: 4  # alphabetically last
        }
        
        # Load model and scaler
        self._load_model(model_path, scaler_path)
    
    def _load_model(self, model_path: str, scaler_path: str):
        """Load the trained model and scaler"""
        try:
            model_file = Path(model_path)
            scaler_file = Path(scaler_path)
            
            if not model_file.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")
            if not scaler_file.exists():
                raise FileNotFoundError(f"Scaler file not found: {scaler_path}")
            
            self.model = joblib.load(model_file)
            self.scaler = joblib.load(scaler_file)
            
            self.model_type = type(self.model).__name__
            self.model_loaded = True
            
            # Try to load model info if available
            info_file = model_file.parent / "model_info.json"
            if info_file.exists():
                with open(info_file, 'r') as f:
                    info = json.load(f)
                    self.model_accuracy = info.get('test_accuracy', None)
            
            logger.info(f"✅ Model loaded successfully: {self.model_type}")
            logger.info(f"✅ Scaler loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {str(e)}")
            raise
    
    def _prepare_features(self, input_data: CodeAnalysisInput) -> np.ndarray:
        """
        Prepare features for model prediction
        
        Args:
            input_data: Code analysis input
            
        Returns:
            Scaled feature array ready for prediction
        """
        # Encode categorical features
        problem_type_encoded = self.problem_type_encoding.get(
            input_data.problem_type, 0
        )
        time_complexity_encoded = self.time_complexity_encoding.get(
            input_data.time_complexity, 0
        )
        
        # Create feature array in correct order
        features = [
            input_data.problem_size,
            input_data.qubits_required,
            input_data.circuit_depth,
            input_data.gate_count,
            input_data.cx_gate_ratio,
            input_data.superposition_score,
            input_data.entanglement_score,
            input_data.memory_requirement_mb,
            problem_type_encoded,
            time_complexity_encoded
        ]
        
        # Convert to DataFrame for consistency
        df = pd.DataFrame([features], columns=self.feature_columns)
        
        # Scale features
        if self.scaler is None:
            raise RuntimeError("Scaler not loaded")
        scaled_features = self.scaler.transform(df)
        
        return scaled_features
    
    def _generate_rationale(
        self,
        input_data: CodeAnalysisInput,
        prediction: int,
        confidence: float,
        quantum_prob: float
    ) -> str:
        """Generate human-readable rationale for the recommendation"""
        
        hardware = "Quantum" if prediction == 1 else "Classical"
        
        # Analyze key factors
        factors = []
        
        if input_data.qubits_required > 0:
            if input_data.qubits_required <= 50:
                factors.append(f"{input_data.qubits_required} qubits (within NISQ limits)")
            else:
                factors.append(f"{input_data.qubits_required} qubits (exceeds current hardware)")
        
        if input_data.superposition_score > 0.7:
            factors.append("high superposition potential")
        
        if input_data.entanglement_score > 0.7:
            factors.append("strong entanglement")
        
        if input_data.circuit_depth > 1000:
            factors.append("deep circuit (noise concerns)")
        
        if input_data.problem_size < 100 and input_data.qubits_required > 0:
            factors.append("small problem (overhead may dominate)")
        
        # Build rationale
        if hardware == "Quantum":
            rationale = f"Recommended for Quantum execution ({confidence:.1%} confidence). "
            if factors:
                rationale += f"Key factors: {', '.join(factors)}. "
            rationale += "Problem exhibits quantum advantage characteristics."
        else:
            rationale = f"Recommended for Classical execution ({confidence:.1%} confidence). "
            if input_data.qubits_required == 0:
                rationale += "Classical algorithm with no quantum operations. "
            elif factors:
                rationale += f"Factors: {', '.join(factors)}. "
            rationale += "Classical approach is more efficient for this workload."
        
        return rationale
    
    def _estimate_cost_and_time(
        self,
        input_data: CodeAnalysisInput,
        hardware: str
    ) -> Tuple[float, float]:
        """
        Estimate execution time and cost
        
        Returns:
            (execution_time_ms, cost_usd)
        """
        if hardware == "Quantum":
            # Quantum cost: based on qubit count and circuit depth
            base_time = 100  # ms
            time_ms = base_time + (input_data.circuit_depth * 0.5) + (input_data.qubits_required * 10)
            
            # Cost: $0.00035 per shot * 1000 shots + setup
            cost_usd = 0.35 + (input_data.qubits_required * 0.01)
        else:
            # Classical cost: based on problem size
            time_ms = input_data.problem_size * 0.01
            cost_usd = 0.001 * (input_data.problem_size / 1000)
        
        return time_ms, cost_usd
    
    def predict(self, input_data: CodeAnalysisInput) -> DecisionEngineResponse:
        """
        Make hardware recommendation based on code analysis
        
        Args:
            input_data: Code analysis input
            
        Returns:
            Decision engine response with recommendation
        """
        try:
            if not self.model_loaded:
                return DecisionEngineResponse(
                    success=False,
                    recommendation=None,
                    alternatives=None,
                    estimated_execution_time_ms=None,
                    estimated_cost_usd=None,
                    error="Model not loaded. Please check configuration."
                )
            
            # Prepare features
            features = self._prepare_features(input_data)
            
            # Make prediction
            if self.model is None:
                raise RuntimeError("Model not loaded")
            prediction = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)[0]
            
            # Extract probabilities
            classical_prob = probabilities[0]
            quantum_prob = probabilities[1]
            confidence = max(probabilities)
            
            # Determine hardware
            hardware = HardwareType.QUANTUM if prediction == 1 else HardwareType.CLASSICAL
            
            # Generate rationale
            rationale = self._generate_rationale(
                input_data, prediction, confidence, quantum_prob
            )
            
            # Estimate cost and time
            exec_time, cost = self._estimate_cost_and_time(input_data, hardware.value)
            
            # Create recommendation
            recommendation = HardwareRecommendation(
                recommended_hardware=hardware,
                confidence=float(confidence),
                quantum_probability=float(quantum_prob),
                classical_probability=float(classical_prob),
                rationale=rationale
            )
            
            # Generate alternatives
            alternatives = []
            if confidence < 0.90:  # If not very confident, provide alternative
                alt_hardware = "Classical" if hardware == HardwareType.QUANTUM else "Quantum"
                alt_confidence = 1.0 - confidence
                alt_time, alt_cost = self._estimate_cost_and_time(input_data, alt_hardware)
                
                alternatives.append({
                    "hardware": alt_hardware,
                    "confidence": float(alt_confidence),
                    "trade_off": f"Alternative option: {alt_time:.0f}ms execution, ${alt_cost:.4f} cost"
                })
            
            return DecisionEngineResponse(
                success=True,
                recommendation=recommendation,
                alternatives=alternatives if alternatives else None,
                estimated_execution_time_ms=float(exec_time),
                estimated_cost_usd=float(cost),
                error=None
            )
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}", exc_info=True)
            return DecisionEngineResponse(
                success=False,
                recommendation=None,
                alternatives=None,
                estimated_execution_time_ms=None,
                estimated_cost_usd=None,
                error=f"Prediction failed: {str(e)}"
            )
    
    def health_check(self) -> Dict:
        """Check service health"""
        return {
            "model_loaded": self.model_loaded,
            "model_type": self.model_type,
            "model_accuracy": self.model_accuracy
        }