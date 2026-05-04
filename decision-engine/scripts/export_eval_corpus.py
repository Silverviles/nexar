"""Export the real-workload evaluation corpus with per-workload 16-feature
vectors and both oracle labels, for reviewer auditability (C5 concern).

Produces:
    decision-engine/artifacts/eval_corpus.csv

Each row: workload_name, 16 features, oracle_a_label, oracle_b_label,
nexar_prediction.

This is the held-out REAL benchmark (QASMBench / MQTBench-sourced), not the
synthetic training corpus. Reviewers can verify the feature distribution of
the evaluation set and the per-sample label assignment without access to the
synthetic training pipeline.

Feature construction replicates `DecisionEngineService._prepare_features`
exactly (see services/decision_engine_service.py) but without loading the
trained ML model, since this script only audits the feature distribution and
oracle labels.
"""
from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ENGINE_DIR = SCRIPT_DIR.parent
REPO_ROOT = ENGINE_DIR.parent
sys.path.insert(0, str(ENGINE_DIR))
sys.path.insert(0, str(SCRIPT_DIR))

spec = importlib.util.spec_from_file_location(
    "raa", SCRIPT_DIR / "routing_accuracy_analysis.py"
)
raa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(raa)

from schemas.decision_engine import ProblemType, TimeComplexity  # noqa: E402
from services.cost_analyser import CostAnalyzer  # noqa: E402
from services.rule_service import RuleBasedSystem  # noqa: E402

CSV_PATH = REPO_ROOT / "benchmarks" / "results" / "pipeline_dataset.csv"
OUT_PATH = REPO_ROOT / "decision-engine" / "artifacts" / "eval_corpus.csv"

# Must match DecisionEngineService.feature_columns exactly.
FEATURE_COLUMNS = [
    "problem_size",
    "qubits_required",
    "circuit_depth",
    "gate_count",
    "cx_gate_ratio",
    "superposition_score",
    "entanglement_score",
    "memory_requirement_mb",
    "problem_type_encoded",
    "time_complexity_encoded",
    "circuit_volume",
    "noise_sensitivity",
    "quantum_overhead_ratio",
    "nisq_viability_score",
    "gate_density",
    "entanglement_factor",
]

# Must match DecisionEngineService encoding maps exactly.
PROBLEM_TYPE_ENCODING = {
    ProblemType.DYNAMIC_PROGRAMMING: 0,
    ProblemType.FACTORIZATION: 1,
    ProblemType.MATRIX_OPS: 2,
    ProblemType.OPTIMIZATION: 3,
    ProblemType.RANDOM_CIRCUIT: 4,
    ProblemType.SEARCH: 5,
    ProblemType.SIMULATION: 6,
    ProblemType.SORTING: 7,
}
TIME_COMPLEXITY_ENCODING = {
    TimeComplexity.EXPONENTIAL: 0,
    TimeComplexity.NLOGN: 1,
    TimeComplexity.POLYNOMIAL: 2,
    TimeComplexity.POLYNOMIAL_SPEEDUP: 3,
    TimeComplexity.QUADRATIC_SPEEDUP: 4,
}


def build_feature_vector(inp) -> list:
    """Replicates DecisionEngineService._prepare_features pre-scaling output."""
    q = inp.qubits_required
    d = inp.circuit_depth
    cx = inp.cx_gate_ratio
    size = inp.problem_size
    gates = inp.gate_count
    ent = inp.entanglement_score

    circuit_volume = q * d
    noise_sensitivity = q * d * cx
    quantum_overhead_ratio = size / max(q, 1)

    nisq_score = 1.0
    if q > 50:
        nisq_score *= 0.1
    if d > 1000:
        nisq_score *= 0.1
    if circuit_volume > 50000:
        nisq_score *= 0.1

    gate_density = gates / max(q, 1)
    entanglement_factor = cx * ent

    problem_type_encoded = PROBLEM_TYPE_ENCODING.get(inp.problem_type, 0)
    time_complexity_encoded = TIME_COMPLEXITY_ENCODING.get(inp.time_complexity, 0)

    return [
        size,
        q,
        d,
        gates,
        cx,
        inp.superposition_score,
        ent,
        inp.memory_requirement_mb,
        problem_type_encoded,
        time_complexity_encoded,
        circuit_volume,
        noise_sensitivity,
        quantum_overhead_ratio,
        nisq_score,
        gate_density,
        entanglement_factor,
    ]


def main() -> None:
    workloads = raa.load_workloads(CSV_PATH)
    print(f"Loaded {len(workloads)} workloads")

    rule_system = RuleBasedSystem()
    cost_analyzer = CostAnalyzer()

    fieldnames = ["workload_name"] + FEATURE_COLUMNS + [
        "oracle_a_label", "oracle_b_label", "nexar_prediction"
    ]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for w in workloads:
            inp = w["input"]
            vec = build_feature_vector(inp)

            la, _ = raa.oracle_algorithmic(
                w["name"], inp.qubits_required, inp.circuit_depth, inp.entanglement_score
            )
            lb, _ = raa.oracle_hardware_viability(
                w["name"], inp.qubits_required, inp.circuit_depth, inp.entanglement_score
            )
            nexar = raa.router_nexar_live(w, rule_system, cost_analyzer)

            row = {"workload_name": w["name"]}
            for col, val in zip(FEATURE_COLUMNS, vec):
                row[col] = val
            row["oracle_a_label"] = la
            row["oracle_b_label"] = lb
            row["nexar_prediction"] = nexar
            writer.writerow(row)

    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
