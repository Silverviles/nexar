import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Optional, Any, List
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
    """Service for ML-based hardware recommendation with Physics-Aware Logic"""
    
    def __init__(self, model_path: str, scaler_path: str):
        """
        Initialize the decision engine service
        """
        self.model: Optional[Any] = None
        self.scaler: Optional[Any] = None
        self.model_loaded: bool = False
        self.model_type: Optional[str] = None
        self.model_accuracy: Optional[float] = None
        
        # ---------------------------------------------------------
        # STEP 1: UPDATE FEATURE COLUMNS
        # This must match the training notebook EXACTLY (16 features)
        # ---------------------------------------------------------
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
            'time_complexity_encoded',
            'circuit_volume',
            'noise_sensitivity',
            'quantum_overhead_ratio',
            'nisq_viability_score',
            'gate_density',
            'entanglement_factor'
        ]
        
        # Encoding maps (Sorted alphabetically to match LabelEncoder behavior)
        self.problem_type_encoding = {
            ProblemType.DYNAMIC_PROGRAMMING: 0,
            ProblemType.FACTORIZATION: 1,
            ProblemType.MATRIX_OPS: 2,
            ProblemType.OPTIMIZATION: 3,
            ProblemType.RANDOM_CIRCUIT: 4,
            ProblemType.SEARCH: 5,
            ProblemType.SIMULATION: 6,
            ProblemType.SORTING: 7
        }
        
        self.time_complexity_encoding = {
            TimeComplexity.EXPONENTIAL: 0,
            TimeComplexity.NLOGN: 1,
            TimeComplexity.POLYNOMIAL: 2,
            TimeComplexity.POLYNOMIAL_SPEEDUP: 3,
            TimeComplexity.QUADRATIC_SPEEDUP: 4
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

    # ---------------------------------------------------------
    # STEP 2: ADD PHYSICS CALCULATION HELPER
    # ---------------------------------------------------------
    def _calculate_physics_features(self, features_dict: Dict[str, Any]) -> list:
        """
        Calculate derived physics features matching the training logic.
        """
        # Extract raw values for readability
        q = features_dict['qubits_required']
        d = features_dict['circuit_depth']
        cx = features_dict['cx_gate_ratio']
        size = features_dict['problem_size']
        gates = features_dict['gate_count']
        ent = features_dict['entanglement_score']

        # 1. Circuit Volume (qubits * depth)
        circuit_volume = q * d

        # 2. Noise Sensitivity
        noise_sensitivity = q * d * cx

        # 3. Quantum Overhead Ratio (avoid div by zero)
        quantum_overhead_ratio = size / max(q, 1)

        # 4. NISQ Viability Score (Logic must match training data generation)
        nisq_score = 1.0
        if q > 50: 
            nisq_score *= 0.1 # Too many qubits for NISQ
        if d > 1000: 
            nisq_score *= 0.1 # Too deep, decoherence risk
        if circuit_volume > 50000: 
            nisq_score *= 0.1 # Volume too high

        # 5. Gate Density
        gate_density = gates / max(q, 1)

        # 6. Entanglement Factor
        entanglement_factor = cx * ent

        # Return only the new features in correct order
        return [
            circuit_volume,
            noise_sensitivity,
            quantum_overhead_ratio,
            nisq_score,
            gate_density,
            entanglement_factor
        ]
    
    # ---------------------------------------------------------
    # STEP 3: UPDATE FEATURE PREPARATION
    # ---------------------------------------------------------
    def _prepare_features(self, input_data: CodeAnalysisInput) -> np.ndarray:
        """
        Prepare features for model prediction (10 Raw + 6 Derived)
        """
        # 1. Encode categorical features
        problem_type_encoded = self.problem_type_encoding.get(
            input_data.problem_type, 0
        )
        time_complexity_encoded = self.time_complexity_encoding.get(
            input_data.time_complexity, 0
        )

        # 2. Create dictionary for easy access to raw values
        features_dict = {
            'problem_size': input_data.problem_size,
            'qubits_required': input_data.qubits_required,
            'circuit_depth': input_data.circuit_depth,
            'gate_count': input_data.gate_count,
            'cx_gate_ratio': input_data.cx_gate_ratio,
            'superposition_score': input_data.superposition_score,
            'entanglement_score': input_data.entanglement_score,
            'memory_requirement_mb': input_data.memory_requirement_mb
        }

        # 3. Calculate Derived Physics Features
        physics_features = self._calculate_physics_features(features_dict)

        # 4. Combine All Features (16 Total)
        final_feature_vector = [
            input_data.problem_size,
            input_data.qubits_required,
            input_data.circuit_depth,
            input_data.gate_count,
            input_data.cx_gate_ratio,
            input_data.superposition_score,
            input_data.entanglement_score,
            input_data.memory_requirement_mb,
            problem_type_encoded,
            time_complexity_encoded,
            *physics_features  # Unpack the 6 new features here
        ]
        
        # 5. Create DataFrame with correct columns
        df = pd.DataFrame([final_feature_vector], columns=self.feature_columns)
        
        # 6. Scale
        if self.scaler is None:
            raise RuntimeError("Scaler not loaded")
            
        # Ensure columns match exactly what the scaler expects
        scaled_features = self.scaler.transform(df)
        
        return scaled_features
    
    # ---------------------------------------------------------
    # STEP 4: UPDATE RATIONALE LOGIC
    # ---------------------------------------------------------
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
        
        # Qubit checks
        if input_data.qubits_required > 0:
            if input_data.qubits_required <= 50:
                factors.append(f"{input_data.qubits_required} qubits (within NISQ limits)")
            else:
                factors.append(f"{input_data.qubits_required} qubits (exceeds current hardware)")
        
        # Quantum scores
        if input_data.superposition_score > 0.7:
            factors.append("high superposition potential")
        
        if input_data.entanglement_score > 0.7:
            factors.append("strong entanglement")
        
        # Problem size check
        if input_data.problem_size < 100 and input_data.qubits_required > 0:
            factors.append("small problem (overhead may dominate)")

        # Physics checks (Volume & Depth)
        circuit_volume = input_data.qubits_required * input_data.circuit_depth
        
        if circuit_volume > 50000:
            factors.append("circuit volume too high for stable execution")
        elif input_data.circuit_depth > 1000:
            factors.append("circuit depth > 1000 (decoherence risk)")
        
        # Build rationale string
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
            
            # Prepare features (Now handles physics calculation internally)
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