# Decision Engine

| | |
|---|---|
| **Directory** | `/decision-engine` |
| **Stack** | FastAPI, Python, scikit-learn, XGBoost |
| **Port** | 8003 |

## Overview

The Decision Engine is responsible for determining the optimal execution target for a given piece of code. It consumes the structured analysis report produced by the Code Analysis Engine, builds a feature vector, and runs it through a trained ML classification model. The output is a routing decision: execute on a real quantum device, a quantum simulator, or a classical machine.

## Feature Vector

The engine constructs a 10-feature input vector from the analysis report. The features capture the key dimensions that influence routing:

- Problem type (algorithm family classification)
- Overall code complexity score
- Qubit count required
- Circuit depth
- Single-qubit gate count
- Multi-qubit gate count
- CX gate ratio
- Available memory estimate
- Time complexity class
- Entanglement score

Each feature is normalised before being passed to the model, ensuring consistent scaling regardless of the input code's size.

## Prediction

The Decision Engine uses trained classification models (scikit-learn pipelines and XGBoost) to predict the optimal execution target. The model outputs one of three classes:

- **Quantum Device** -- The code is suitable for execution on real quantum hardware, with expected quantum advantage.
- **Quantum Simulator** -- The code involves quantum operations but is better served by a simulator (e.g., too many qubits for available hardware, or noise would degrade results).
- **Classical** -- The code does not benefit from quantum execution and should run on a classical machine.

The prediction includes a confidence score, allowing downstream services to handle low-confidence decisions appropriately.

## Model Metadata

The engine exposes metadata about the active model for operator inspection and debugging. This includes the model version identifier, training date, feature configuration, and performance metrics from the most recent evaluation run. Operators can use this information to verify that the expected model is deployed and performing within acceptable thresholds.

## API

The Decision Engine exposes the following endpoints:

- **`/predict`** -- Accepts an analysis report and returns the routing decision with confidence score.
- **`/health`** -- Returns the service health status, used by load balancers and monitoring systems.
- **`/model-info`** -- Returns metadata about the currently loaded model, including version, configuration, and evaluation metrics.
