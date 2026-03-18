# Decision Engine — Research Proposal

**Researcher:** Prasad H G A T

## Research Objective

Design an ML-based decision system that predicts the optimal execution platform (quantum device, quantum simulator, or classical hardware) based on code analysis metrics.

## Key Research Questions

- What features best predict quantum advantage for a given algorithm?
- How can classification models be trained to route code between quantum and classical backends?
- How should model metadata be exposed for transparency and operability?

## Approach

Train classification models (scikit-learn, XGBoost) on a feature vector including problem type, complexity, qubit count, gate profile, memory, and time complexity. Expose model version and configuration via API.
