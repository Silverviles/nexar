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

from .cost_analyser import CostAnalyzer
from .rule_service import RuleBasedSystem
from .decision_merger import DecisionMerger

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
        
        # Initialize sub-components
        self.cost_analyzer = CostAnalyzer()
        self.rule_system = RuleBasedSystem()
        self.decision_merger = DecisionMerger()
        
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
    
    def predict(self, input_data: CodeAnalysisInput, budget_limit_usd: Optional[float] = None) -> DecisionEngineResponse:
        """
        Make hardware recommendation based on code analysis, rules, and cost
        
        Args:
            input_data: Code analysis input
            budget_limit_usd: Optional budget limit in USD
            
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
            
            # ---------------------------------------------------------
            # 1. ML MODEL PREDICTION
            # ---------------------------------------------------------
            # Prepare features (Now handles physics calculation internally)
            features = self._prepare_features(input_data)
            
            # Make prediction
            if self.model is None:
                raise RuntimeError("Model not loaded")
            prediction = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)[0]
            
            # Extract probabilities
            classical_prob = float(probabilities[0])
            quantum_prob = float(probabilities[1])
            confidence = float(max(probabilities))
            
            # Determine ML hardware recommendation
            ml_hardware = HardwareType.QUANTUM if prediction == 1 else HardwareType.CLASSICAL
            
            ml_decision = {
                'hardware': ml_hardware,
                'confidence': confidence,
                'quantum_probability': quantum_prob,
                'classical_probability': classical_prob,
                'rationale': f"ML Model predicts {ml_hardware.value} with {confidence:.1%} confidence"
            }
            
            # ---------------------------------------------------------
            # 2. RULE-BASED VALIDATION
            # ---------------------------------------------------------
            rule_decision = self.rule_system.evaluate(input_data)
            
            # ---------------------------------------------------------
            # 3. COST ANALYSIS
            # ---------------------------------------------------------
            cost_analysis = self.cost_analyzer.analyze(
                input_data, 
                ml_hardware, 
                budget_limit_usd
            )
            
            # ---------------------------------------------------------
            # 4. DECISION MERGING
            # ---------------------------------------------------------
            final_recommendation = self.decision_merger.merge(
                ml_decision,
                rule_decision,
                cost_analysis
            )
            
            # ---------------------------------------------------------
            # 5. CONSTRUCT RESPONSE
            # ---------------------------------------------------------
            
            # Determine alternatives
            alternatives = []
            
            # If recommendation is Quantum, offer Classical as alternative (and vice versa)
            rec_hw = final_recommendation.recommended_hardware
            alt_hw = HardwareType.CLASSICAL if rec_hw == HardwareType.QUANTUM else HardwareType.QUANTUM
            
            # Get cost/time for alternative
            if alt_hw == HardwareType.QUANTUM:
                alt_cost = cost_analysis['quantum_cost_usd']
                alt_time = cost_analysis['quantum_time_ms']
            else:
                alt_cost = cost_analysis['classical_cost_usd']
                alt_time = cost_analysis['classical_time_ms']
                
            alternatives.append({
                "hardware": alt_hw.value,
                "confidence": 1.0 - final_recommendation.confidence,
                "trade_off": f"Alternative: {alt_time:.0f}ms execution, ${alt_cost:.4f} cost"
            })
            
            # Get estimated cost/time for recommended hardware
            if rec_hw == HardwareType.QUANTUM:
                est_cost = cost_analysis['quantum_cost_usd']
                est_time = cost_analysis['quantum_time_ms']
            else:
                est_cost = cost_analysis['classical_cost_usd']
                est_time = cost_analysis['classical_time_ms']
            
            return DecisionEngineResponse(
                success=True,
                recommendation=final_recommendation,
                alternatives=alternatives,
                estimated_execution_time_ms=float(est_time),
                estimated_cost_usd=float(est_cost),
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