# Code Analysis Engine

| | |
|---|---|
| **Directory** | `/code-analysis-engine` |
| **Stack** | FastAPI, Python, CodeBERT, scikit-learn, tree-sitter |
| **Port** | 8002 |

## Overview

The Code Analysis Engine is the analytical core of the Nexar platform. It accepts raw source code, determines the programming language, computes a comprehensive set of classical and quantum metrics, classifies the algorithm, and returns a structured analysis report. This report serves as the primary input to the Decision Engine, which uses it to determine the optimal execution target.

## Language Detection

The engine identifies the programming language of submitted code, supporting:

- **Python** -- General-purpose Python code
- **Qiskit** -- IBM's quantum computing SDK (Python-based)
- **Cirq** -- Google's quantum computing framework (Python-based)
- **Q#** -- Microsoft's quantum programming language
- **OpenQASM** -- Open Quantum Assembly Language

Each detection result includes a **confidence score** indicating the engine's certainty. When quantum-specific imports or syntax are present, the detector distinguishes between plain Python and quantum framework code.

## Classical Metrics

For all submitted code, the engine computes classical complexity metrics through AST (Abstract Syntax Tree) analysis:

- **Cyclomatic Complexity** -- Measures the number of independent paths through the code, indicating decision complexity.
- **Nesting Depth** -- Tracks the maximum depth of nested control structures (loops, conditionals, try/except blocks).
- **Loop and Conditional Counts** -- Enumerates the number of for/while loops and if/else branches.
- **Time Complexity** -- Estimates asymptotic time complexity (e.g., O(n), O(n log n), O(n^2)) by analysing loop structures and recursive patterns.
- **Space Complexity** -- Estimates memory usage growth based on data structure allocations and recursive call depth.

## Quantum Metrics

When the code involves quantum operations, the engine extracts additional metrics:

- **Qubit Requirements** -- The number of qubits needed to execute the circuit.
- **Circuit Depth** -- Computed via a dependency graph of gate operations, representing the critical path length.
- **Gate Counts** -- Total number of quantum gates, broken down by type (Hadamard, CNOT, Toffoli, rotation gates, etc.).
- **Superposition and Entanglement Scoring** -- Quantifies the degree of superposition (Hadamard density) and entanglement (multi-qubit gate density) in the circuit.
- **CX Gate Ratio** -- The proportion of CNOT (CX) gates relative to total gates, an important factor in estimating noise impact on real hardware.

## Algorithm Classification

The engine classifies the submitted code's algorithm using a three-tier approach, falling through to the next tier when confidence is insufficient:

1. **CodeBERT Transformer** -- A fine-tuned CodeBERT model analyses the code's semantic structure and classifies it against a taxonomy of known algorithm families (e.g., search, optimisation, factorisation, simulation). This tier provides the highest accuracy when confident.

2. **ML Ensemble Fallback** -- When the transformer's confidence falls below a threshold, an ensemble of scikit-learn classifiers (trained on extracted code features) provides a secondary classification.

3. **Rule-Based Pattern Matching** -- As a final fallback, the engine applies heuristic pattern-matching rules that look for characteristic code structures (e.g., nested loops for matrix multiplication, recursive divide-and-conquer patterns).

## Key Modules

The engine is organised into the following core modules:

- **language_detector** -- Identifies the programming language and quantum framework.
- **ast_builder** -- Parses source code into an Abstract Syntax Tree using tree-sitter.
- **complexity_analyzer** -- Computes classical complexity metrics from the AST.
- **quantum_analyzer** -- Extracts quantum-specific metrics from quantum circuits.
- **algorithm_detector** -- Orchestrates the three-tier classification pipeline.
- **codebert_algorithm_classifier** -- Wraps the fine-tuned CodeBERT model for algorithm classification.
- **canonical_ir_builder** -- Constructs a canonical intermediate representation for cross-language analysis.

## Optimization Suggestions

Alongside the analysis report, the engine generates **actionable optimization recommendations**. Each suggestion identifies a specific area of improvement (e.g., reducing circuit depth, minimising CX gate usage, restructuring nested loops) and includes an **improvement estimate** quantifying the expected benefit. These suggestions help users refine their code before execution.
