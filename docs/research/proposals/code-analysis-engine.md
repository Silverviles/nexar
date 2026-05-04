# Code Analysis Engine — Research Proposal

**Researcher:** Jayasinghe Y L

## Research Objective

Build a multi-dimensional code analysis pipeline that detects programming languages, computes classical and quantum complexity metrics, and classifies algorithms using a three-tier ML approach.

## Key Research Questions

- How can AST-based analysis be combined with ML classifiers for accurate algorithm detection?
- What metrics best characterize quantum suitability of code?
- How can CodeBERT be fine-tuned for quantum algorithm classification?

## Approach

Combine tree-sitter-based AST parsing with CodeBERT transformer models and scikit-learn ensemble classifiers. Analyse both classical metrics (cyclomatic complexity, nesting) and quantum metrics (qubit count, circuit depth, entanglement scoring).

