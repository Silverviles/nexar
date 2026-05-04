# AI Code Converter

| | |
|---|---|
| **Directory** | `/ai-code-converter` |
| **Stack** | FastAPI, Python, Transformers, Qiskit, Cirq |
| **Port** | 8001 |

## Overview

The AI Code Converter bridges classical and quantum code within the Nexar platform. It translates classical Python into quantum circuits, evaluates code for quantum suitability, executes generated circuits, and returns results. This service is invoked when the Decision Engine determines that code should run on a quantum backend but the submitted code is classical.

## Code Translation

The converter translates classical Python code into quantum circuits targeting Qiskit or Cirq. Translation is powered by a transformer-based generation model that has been trained on paired classical-quantum code examples. The model analyses the logic structure of the input code and produces an equivalent quantum circuit that preserves the computational intent while leveraging quantum parallelism where applicable.

## Pattern Recognition

Before translation, the converter scans the input code for well-known quantum-amenable patterns. Recognised patterns are mapped to established quantum algorithms:

- **Linear search** maps to **Grover's algorithm**, offering quadratic speedup for unstructured search problems.
- **Combinatorial optimisation** maps to **QAOA** (Quantum Approximate Optimization Algorithm), targeting problems like MaxCut and constraint satisfaction.
- **Integer factorisation** maps to **Shor's algorithm**, providing exponential speedup over classical factorisation methods.

When a pattern is detected, the converter uses the corresponding quantum algorithm template rather than a generic translation, producing more efficient circuits.

## Suitability Scoring

For every input, the converter produces a suitability assessment indicating how well the code maps to quantum execution:

- **HIGH** -- The code contains patterns with known quantum advantage; significant speedup is expected.
- **MEDIUM** -- The code can be expressed as a quantum circuit, but the advantage over classical execution is modest or depends on problem scale.
- **LOW** -- The code does not benefit meaningfully from quantum execution.

Each rating is accompanied by a **confidence score** and an **expected speedup estimate** (e.g., quadratic, exponential, or negligible), giving users clear expectations before committing to execution.

## Circuit Execution

The converter can execute generated quantum circuits directly, returning:

- **Measurement distributions** -- The probability distribution over measurement outcomes across the configured number of shots.
- **Performance metrics** -- Execution time, shot count, circuit depth after transpilation, and gate counts on the target backend.

This capability allows users to test converted circuits without leaving the conversion interface.

## Logic Extraction

Before translation, the converter applies a logic extraction step that strips boilerplate code (imports, I/O handling, argument parsing, logging) to isolate the **core computational logic**. This ensures that the translation model focuses on the algorithmically meaningful portion of the code, producing cleaner and more efficient quantum circuits.
