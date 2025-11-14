#!/usr/bin/env python3
"""
Quick model generator for development and testing
Creates mock trained models for the Decision Engine when real models aren't available
"""

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import json

def create_mock_model():
    """Create a mock trained model for development"""
    
    # Create simple mock training data
    np.random.seed(42)
    n_samples = 1000
    
    # Feature order matching DecisionEngineService.feature_columns
    X = np.random.rand(n_samples, 10)
    
    # Simple heuristic: quantum if qubits > 0 and high quantum scores
    y = []
    for i in range(n_samples):
        qubits = int(X[i, 1] * 30)  # qubits_required (0-30)
        superposition = X[i, 5]      # superposition_score
        entanglement = X[i, 6]       # entanglement_score
        
        # Simple decision rule
        if qubits > 0 and (superposition > 0.6 or entanglement > 0.6):
            y.append(1)  # Quantum
        else:
            y.append(0)  # Classical
    
    y = np.array(y)
    
    # Train simple model
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    
    # Create scaler
    scaler = StandardScaler()
    scaler.fit(X)
    
    # Save model and scaler
    models_dir = Path(__file__).parent / "ml_models"
    models_dir.mkdir(exist_ok=True)
    
    joblib.dump(model, models_dir / "decision_engine_model.pkl")
    joblib.dump(scaler, models_dir / "feature_scaler.pkl")
    
    # Save model info
    accuracy = model.score(X, y)
    model_info = {
        "model_type": "RandomForestClassifier",
        "test_accuracy": float(accuracy),
        "n_features": X.shape[1],
        "n_samples": n_samples,
        "created_for": "development_testing"
    }
    
    with open(models_dir / "model_info.json", "w") as f:
        json.dump(model_info, f, indent=2)
    
    print(f"✅ Mock model created successfully!")
    print(f"📊 Training accuracy: {accuracy:.3f}")
    print(f"💾 Saved to: {models_dir}")

if __name__ == "__main__":
    create_mock_model()