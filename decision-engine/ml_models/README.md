# ML Models Directory

This directory contains the trained machine learning models and preprocessing components for the Decision Engine.

## Required Files:
- `decision_engine_model.pkl` - Trained classifier model 
- `feature_scaler.pkl` - Feature scaler for preprocessing
- `model_info.json` - Model metadata (optional)

## Model Training:
Use the training scripts in the parent directory to generate these model files.

## Development:
For development without trained models, the service will return appropriate error messages and can be tested with mock predictions.