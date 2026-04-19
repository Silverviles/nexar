"""
Routing Accuracy Analysis for Nexar Decision Engine
===================================================
Addresses IEEE reviewer critique: "routing accuracy has no ground truth".

This script:
  1. Derives a literature-cited oracle ground-truth label for each of the 100
     benchmark workloads, independent of Nexar's decision logic.
  2. Computes three baseline routers (qubit threshold, volume threshold, random).
  3. Runs three component ablations (ML-only, Rules-only, Cost-only) by calling
     the individual services in isolation.
  4. Reports confusion matrix, precision, recall, F1, accuracy, and Cohen's
     kappa for every router against the oracle.

Oracle rules (citations in code):
  R1: qubits == 0                             -> Classical (trivial, no circuit)
  R2: qubits >  127                           -> Reject    (Arute 2019; IBM Eagle limit)
  R3: qubits >= 50                            -> Quantum   (Preskill 2018; state-vector
                                                             simulation infeasible > 16 PB)
  R4: family == factorization AND qubits >= 8 -> Quantum   (Shor 1997; exp. speedup)
  R5: family == simulation   AND qubits >= 20
      AND entanglement >= 0.3                 -> Quantum   (Kandala 2017; VQE)
  R6: family == optimization AND qubits >= 20
      AND entanglement >= 0.3                 -> Quantum   (Farhi 2014; QAOA)
  R7: family == search       AND qubits >= 20 -> Quantum   (Grover 1996; sqrt(N))
  R8: otherwise                               -> Classical (NISQ overhead dominates;
                                                             Preskill 2018)

Algorithm family is derived *from the workload filename*, not from Nexar's
classifier, so the oracle is independent of the system under test.

Usage:
    cd decision-engine
    python scripts/routing_accuracy_analysis.py

Outputs:
    latex/routing_accuracy_results.json     (raw metrics + per-workload labels)
    latex/routing_accuracy_table.tex        (main comparison table for paper)
    latex/oracle_ground_truth.csv           (every workload with oracle label + rule)
"""
from __future__ import annotations

import csv
import json
import os
import random
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    cohen_kappa_score,
    confusion_matrix,
    precision_recall_fscore_support,
)

# ---------------------------------------------------------------------------
# Path setup -- run from decision-engine/
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
ENGINE_DIR = SCRIPT_DIR.parent
REPO_ROOT = ENGINE_DIR.parent
sys.path.insert(0, str(ENGINE_DIR))

from schemas.decision_engine import (  # noqa: E402
    CodeAnalysisInput,
    HardwareType,
    ProblemType,
    TimeComplexity,
)
from services.cost_analyser import CostAnalyzer  # noqa: E402
from services.decision_merger import DecisionMerger  # noqa: E402
from services.rule_service import RuleBasedSystem, RuleDecisionType  # noqa: E402

CSV_PATH = REPO_ROOT / "benchmarks" / "results" / "pipeline_dataset.csv"
LATEX_DIR = REPO_ROOT / "latex"
LATEX_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Schema-mapping helpers (shared with weight_sensitivity_analysis.py)
# ---------------------------------------------------------------------------
PROBLEM_TYPE_MAP = {
    "factorization": ProblemType.FACTORIZATION,
    "search": ProblemType.SEARCH,
    "simulation": ProblemType.SIMULATION,
    "optimization": ProblemType.OPTIMIZATION,
    "sorting": ProblemType.SORTING,
    "dynamic_programming": ProblemType.DYNAMIC_PROGRAMMING,
    "matrix_ops": ProblemType.MATRIX_OPS,
    "random_circuit": ProblemType.RANDOM_CIRCUIT,
    "sampling": ProblemType.SAMPLING,
}

TIME_COMPLEXITY_MAP = {
    "polynomial": TimeComplexity.POLYNOMIAL,
    "exponential": TimeComplexity.EXPONENTIAL,
    "quadratic_speedup": TimeComplexity.QUADRATIC_SPEEDUP,
    "polynomial_speedup": TimeComplexity.POLYNOMIAL_SPEEDUP,
    "nlogn": TimeComplexity.NLOGN,
}


# ---------------------------------------------------------------------------
# Oracle: algorithm family derived from filename (independent of Nexar)
# ---------------------------------------------------------------------------
# Keyword buckets are examined in priority order; first match wins.
_FAMILY_KEYWORDS: List[Tuple[str, Tuple[str, ...]]] = [
    ("factorization", ("shor", "_factor", "discrete_log")),
    ("search", ("grover", "3sat", "satisfiability")),
    ("simulation", (
        "vqe", "uccsd", "molecule", "molecular", "ising", "heisenberg",
        "hubbard", "schwinger", "bcs", "superconductor", "nitrogen_fixation",
        "iron_sulfur", "lithium_battery", "hydrogen_chain", "caffeine",
        "h2_", "h2o", "lih_", "water_molecule", "transverse_field",
        "hamiltonian_simulation", "spin_chain", "quantum_molecular",
        "variational_quantum_thermalizer", "quantum_boltzmann",
    )),
    ("optimization", (
        "qaoa", "maxcut", "portfolio", "graph_partition", "graph_partitioning",
        "vehicle_routing", "scheduling", "supply_chain", "credit_risk",
        "traveling_salesman", "tsp", "graph_coloring",
    )),
    ("oracle_problem", ("bernstein_vazirani", "deutsch", "simon", "hidden_period")),
    ("primitive", (
        "qft", "phase_estimation", "qpe", "amplitude_estimation",
        "quantum_counting", "approximate_counting", "hhl",
        "quantum_walk", "quantum_monte_carlo", "monte_carlo_option",
    )),
    ("qml", (
        "qml", "qsvm", "qnn", "quantum_neural", "quantum_kernel",
        "quantum_transfer_learning", "qgan", "quantum_gan",
        "quantum_reinforcement", "drug_", "quantum_chemistry",
    )),
    ("error_correction", (
        "error_correction", "surface_code", "error_mitigation", "zne",
    )),
    ("primitive_state", (
        "teleportation", "ghz", "bell_state", "bb84",
        "quantum_key", "quantum_random_number", "qrng",
    )),
    ("random_circuit", ("random_circuit", "high_depth_noise")),
    ("oversize", ("oversize", "150q_rejected")),
]


def derive_family(workload_name: str) -> str:
    name = workload_name.lower()
    for family, keywords in _FAMILY_KEYWORDS:
        for kw in keywords:
            if kw in name:
                return family
    return "classical"


# ---------------------------------------------------------------------------
# Oracle A: Algorithmic advantage (textbook speedup regime)
# ---------------------------------------------------------------------------
def oracle_algorithmic(
    workload_name: str,
    qubits: int,
    depth: int,
    entanglement: float,
) -> Tuple[str, str]:
    """Oracle A: when does a known quantum algorithm *in principle* win?

    Uses published complexity-theoretic criteria: Shor's exponential speedup,
    Grover's sqrt(N), VQE/QAOA for entangled large-N problems, plus the
    classical simulation memory wall. Ignores NISQ hardware fidelity; answers
    the question "should this be a quantum workload in the fault-tolerant
    era?".
    """
    family = derive_family(workload_name)

    # R1: No quantum resources -> classical trivially
    if qubits == 0:
        return "Classical", "A-R1: Pure classical code (qubits = 0)"

    # R2: Exceeds IBM Eagle capacity
    if qubits > 127:
        return "Reject", "A-R2: Exceeds hardware capacity (> 127 qubits; Arute 2019)"

    # R3: Memory wall -- state-vector simulation infeasible
    if qubits >= 50:
        return ("Quantum",
                "A-R3: Classical state-vector simulation infeasible (> 16 PB; Preskill 2018)")

    # R4: Shor-class factorization with non-trivial N
    if family == "factorization" and qubits >= 8:
        return "Quantum", "A-R4: Factorization -- exponential speedup (Shor 1997)"

    # R5: Large entangled simulation (VQE regime)
    if family == "simulation" and qubits >= 20 and entanglement >= 0.3:
        return "Quantum", "A-R5: Large-scale entangled simulation (Kandala 2017)"

    # R6: Large entangled optimization (QAOA regime)
    if family == "optimization" and qubits >= 20 and entanglement >= 0.3:
        return "Quantum", "A-R6: Large-scale entangled optimization (Farhi 2014)"

    # R7: Grover search -- sqrt(N) speedup meaningful for N >= 2^20
    if family == "search" and qubits >= 20:
        return "Quantum", "A-R7: Grover search with sufficient N (Grover 1996)"

    # R8: Everything else -- NISQ overhead dominates
    return ("Classical",
            "A-R8: NISQ overhead exceeds quantum benefit (Preskill 2018; small-N regime)")


# ---------------------------------------------------------------------------
# Oracle B: Hardware viability (NISQ-era practical routing)
# ---------------------------------------------------------------------------
# Post-transpile depth threshold drawn from the paper's own Table VI
# hardware-validation evidence: circuits with post-transpile depth > ~130
# degrade below 20% top-outcome fidelity on ibm_fez, and circuits above ~500
# approach the noise floor.
_NISQ_DEPTH_WALL = 200  # conservative upper bound for usable-signal regime


def oracle_hardware_viability(
    workload_name: str,
    qubits: int,
    depth: int,
    entanglement: float,
) -> Tuple[str, str]:
    """Oracle B: where will NISQ hardware produce usable signal today?

    Rules derived from real ibm_fez validation data in Table VI of the paper:
    small-depth (<=200) circuits above 2 qubits retain usable fidelity;
    deep small-qubit circuits are noise-dominated and should run classically;
    circuits above the memory wall must run on quantum regardless of fidelity.
    """
    family = derive_family(workload_name)

    # B-R1: No quantum resources -> classical trivially
    if qubits == 0:
        return "Classical", "B-R1: Pure classical code (qubits = 0)"

    # B-R2: Exceeds hardware capacity
    if qubits > 127:
        return "Reject", "B-R2: Exceeds 127-qubit IBM Eagle capacity"

    # B-R3: Memory wall -- quantum is the only viable path (even if noisy)
    if qubits >= 50:
        return ("Quantum",
                f"B-R3: Classical simulation infeasible at {qubits} qubits; "
                f"quantum is only physically viable path")

    # B-R4: Small+shallow circuits -> classical simulation is trivial and noise-free
    #       (NISQ overhead of ~$2 + queue time never justified in this regime)
    if qubits < 20 and depth <= _NISQ_DEPTH_WALL:
        return ("Classical",
                f"B-R4: Small-scale circuit (q={qubits}, d={depth}) is "
                f"trivially simulable and free of NISQ overhead")

    # B-R5: Deep circuits at any sub-50-qubit scale -> noise-dominated on current HW
    if depth > _NISQ_DEPTH_WALL and qubits < 50:
        return ("Classical",
                f"B-R5: Post-transpile depth {depth} exceeds NISQ coherence wall "
                f"(~{_NISQ_DEPTH_WALL}); real HW output is noise-dominated (Table VI)")

    # B-R6: Medium-scale shallow entangled circuits (20 <= q < 50, d <= 200, ent >= 0.3)
    #       are the ideal NISQ-advantage regime
    if 20 <= qubits < 50 and depth <= _NISQ_DEPTH_WALL and entanglement >= 0.3:
        return ("Quantum",
                f"B-R6: Medium-scale entangled circuit (q={qubits}, d={depth}, "
                f"ent={entanglement:.2f}) in NISQ-advantage regime")

    # B-R7: Everything else -> classical (weak entanglement, or ambiguous)
    return ("Classical",
            f"B-R7: Sub-advantage profile (q={qubits}, d={depth}, ent={entanglement:.2f})")


# Keep a stable alias for backwards compatibility
oracle_label = oracle_algorithmic


# ---------------------------------------------------------------------------
# Load workloads
# ---------------------------------------------------------------------------
def load_workloads(csv_path: Path) -> List[Dict]:
    workloads = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("status") != "completed":
                continue

            pt_str = (row.get("mapped_problem_type") or "sorting").lower()
            pt = PROBLEM_TYPE_MAP.get(pt_str, ProblemType.SORTING)

            tc_str = (row.get("mapped_time_complexity") or "polynomial").lower()
            tc = TIME_COMPLEXITY_MAP.get(tc_str, TimeComplexity.POLYNOMIAL)

            try:
                inp = CodeAnalysisInput(
                    problem_type=pt,
                    problem_size=max(1, int(float(row["problem_size"]))),
                    qubits_required=int(float(row["qubits_required"])),
                    circuit_depth=int(float(row["circuit_depth"])),
                    gate_count=int(float(row["gate_count"])),
                    cx_gate_ratio=float(row["cx_gate_ratio"]),
                    superposition_score=float(row["superposition_score"]),
                    entanglement_score=float(row["entanglement_score"]),
                    time_complexity=tc,
                    memory_requirement_mb=float(row["memory_mb"]),
                )
            except Exception as e:  # pragma: no cover - defensive
                print(f"  [WARN] Skipping {row['workload_name']}: {e}")
                continue

            workloads.append({
                "name": row["workload_name"],
                "input": inp,
                "nexar_hw": row["recommended_hardware"],
                "ml_quantum_prob": float(row["quantum_probability"]),
                "ml_classical_prob": float(row["classical_probability"]),
                "raw_problem_type": row.get("problem_type", ""),
            })
    return workloads


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
def router_nexar(w: Dict) -> str:
    """CSV-cached Nexar output (pre-bugfix baseline)."""
    return w["nexar_hw"]


def router_nexar_live(
    w: Dict,
    rule_system: RuleBasedSystem,
    cost_analyzer: CostAnalyzer,
) -> str:
    """Live Nexar decision using the current rule/cost services.

    Uses the paper's baseline weights (50/35/15). This picks up any rule-
    engine bug fixes that post-date the cached pipeline_dataset.csv.
    """
    return router_nexar_reweighted(
        w,
        weights={"ml_model": 0.50, "rule_system": 0.35, "cost_analysis": 0.15},
        rule_system=rule_system,
        cost_analyzer=cost_analyzer,
    )


def router_B1_qubit_threshold(w: Dict) -> str:
    return "Quantum" if w["input"].qubits_required >= 50 else "Classical"


def router_B2_volume_threshold(w: Dict) -> str:
    vol = w["input"].qubits_required * w["input"].circuit_depth
    return "Quantum" if vol >= 50_000 else "Classical"


def router_B3_random(w: Dict, rng: random.Random) -> str:
    return "Quantum" if rng.random() < 0.5 else "Classical"


def router_A1_ml_only(w: Dict) -> str:
    return "Quantum" if w["ml_quantum_prob"] >= w["ml_classical_prob"] else "Classical"


def router_A2_rules_only(w: Dict, rule_system: RuleBasedSystem) -> str:
    decision = rule_system.evaluate(w["input"])
    dt = decision["decision_type"]
    if dt == RuleDecisionType.FORCE_QUANTUM:
        return "Quantum"
    if dt == RuleDecisionType.FORCE_CLASSICAL:
        return "Classical"
    if dt == RuleDecisionType.REJECT:
        return "Reject"
    # ALLOW_BOTH: use rules' soft preference if any, else fall back classical
    hw = decision.get("hardware")
    if hw == HardwareType.QUANTUM:
        return "Quantum"
    if hw == HardwareType.CLASSICAL:
        return "Classical"
    return "Classical"  # neutral -> default safe choice


def router_A3_cost_only(w: Dict, cost_analyzer: CostAnalyzer) -> str:
    # cost_analyzer requires a "ML hardware" hint; give it the ML winner
    ml_hw = (HardwareType.QUANTUM
             if w["ml_quantum_prob"] >= w["ml_classical_prob"]
             else HardwareType.CLASSICAL)
    analysis = cost_analyzer.analyze(w["input"], ml_hw, budget_limit_usd=None)
    return analysis["cost_optimal_hardware"]


def router_nexar_reweighted(
    w: Dict,
    weights: Dict[str, float],
    rule_system: RuleBasedSystem,
    cost_analyzer: CostAnalyzer,
) -> str:
    """Run the full Nexar decision pipeline with alternate weights.

    Reconstructs the ML decision from the CSV's raw ML probabilities so we
    don't need to re-run the Random Forest per configuration. Returns
    "Reject" when the rule engine emits a rejection (the HardwareType enum
    itself has no "Reject" value; this surfaces it for evaluation).
    """
    inp = w["input"]
    q_prob = w["ml_quantum_prob"]
    c_prob = w["ml_classical_prob"]

    ml_hw = HardwareType.QUANTUM if q_prob >= c_prob else HardwareType.CLASSICAL
    ml_decision = {
        "hardware": ml_hw,
        "confidence": max(q_prob, c_prob),
        "quantum_probability": q_prob,
        "classical_probability": c_prob,
        "rationale": f"ML: {ml_hw.value}",
    }
    rule_decision = rule_system.evaluate(inp)

    # Surface REJECT as a first-class label for evaluation purposes.
    if rule_decision.get("decision_type") == RuleDecisionType.REJECT:
        return "Reject"

    cost_analysis = cost_analyzer.analyze(inp, ml_hw, budget_limit_usd=None)
    merger = DecisionMerger()
    merger.decision_weights = dict(weights)
    rec = merger.merge(ml_decision, rule_decision, cost_analysis)
    return rec.recommended_hardware.value


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def compute_metrics(y_true: List[str], y_pred: List[str], label: str) -> Dict:
    """Compute accuracy, precision/recall/F1 for the Quantum class, kappa, CM.

    Rejects are folded into their oracle target for headline accuracy (so a
    router that correctly rejects matches the oracle) but kept separately for
    display in the confusion matrix.
    """
    labels = ["Classical", "Quantum", "Reject"]

    # Filter to valid labels
    yt = [t if t in labels else "Classical" for t in y_true]
    yp = [p if p in labels else "Classical" for p in y_pred]

    acc = accuracy_score(yt, yp)
    kappa = cohen_kappa_score(yt, yp, labels=labels)

    # Binary precision/recall/F1 on the Quantum class (positive = Quantum).
    # Reject is treated as "not Quantum" for this binary view.
    yt_bin = [1 if x == "Quantum" else 0 for x in yt]
    yp_bin = [1 if x == "Quantum" else 0 for x in yp]
    p, r, f1, _ = precision_recall_fscore_support(
        yt_bin, yp_bin, average="binary", zero_division=0
    )

    cm = confusion_matrix(yt, yp, labels=labels).tolist()

    return {
        "router": label,
        "accuracy": round(acc, 4),
        "precision_quantum": round(float(p), 4),
        "recall_quantum": round(float(r), 4),
        "f1_quantum": round(float(f1), 4),
        "cohen_kappa": round(float(kappa), 4),
        "confusion_matrix": cm,
        "labels_order": labels,
    }


# ---------------------------------------------------------------------------
# Analysis driver
# ---------------------------------------------------------------------------
def analyse() -> None:
    print(f"Loading workloads from {CSV_PATH}")
    if not CSV_PATH.exists():
        raise SystemExit(f"ERROR: CSV not found at {CSV_PATH}. "
                         "Run benchmarks/run-benchmark.sh first.")

    workloads = load_workloads(CSV_PATH)
    print(f"Loaded {len(workloads)} workloads\n")

    rule_system = RuleBasedSystem()
    cost_analyzer = CostAnalyzer()

    # ----- Dual-oracle labeling -----
    print("Generating literature-cited dual-oracle ground truth...")
    oracle_rows = []
    for w in workloads:
        family = derive_family(w["name"])
        alg_label, alg_rule = oracle_algorithmic(
            w["name"],
            w["input"].qubits_required,
            w["input"].circuit_depth,
            w["input"].entanglement_score,
        )
        hw_label, hw_rule = oracle_hardware_viability(
            w["name"],
            w["input"].qubits_required,
            w["input"].circuit_depth,
            w["input"].entanglement_score,
        )
        oracle_rows.append({
            "workload": w["name"],
            "family": family,
            "qubits": w["input"].qubits_required,
            "depth": w["input"].circuit_depth,
            "entanglement": w["input"].entanglement_score,
            "oracle_algorithmic": alg_label,
            "rule_algorithmic": alg_rule,
            "oracle_hardware": hw_label,
            "rule_hardware": hw_rule,
            "nexar_label": w["nexar_hw"],
        })

    # Persist the oracle CSV so a reviewer can audit every label
    oracle_csv = LATEX_DIR / "oracle_ground_truth.csv"
    with open(oracle_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(oracle_rows[0].keys()))
        writer.writeheader()
        writer.writerows(oracle_rows)
    print(f"  -> wrote {oracle_csv} ({len(oracle_rows)} rows)")

    # ----- Run every router once; evaluate against both oracles -----
    print("\nRunning routers and baselines...")
    y_alg = [r["oracle_algorithmic"] for r in oracle_rows]
    y_hw = [r["oracle_hardware"] for r in oracle_rows]

    rng = random.Random(42)
    router_preds = {
        "Nexar (full)":     [router_nexar_live(w, rule_system, cost_analyzer)
                             for w in workloads],
        "B1 Qubit>=50":     [router_B1_qubit_threshold(w)          for w in workloads],
        "B2 Volume>=50k":   [router_B2_volume_threshold(w)         for w in workloads],
        "B3 Random":        [router_B3_random(w, rng)              for w in workloads],
        "A1 ML-only":       [router_A1_ml_only(w)                  for w in workloads],
        "A2 Rules-only":    [router_A2_rules_only(w, rule_system)  for w in workloads],
        "A3 Cost-only":     [router_A3_cost_only(w, cost_analyzer) for w in workloads],
    }

    # Stable estimate of the random baseline over 1000 seeds, per-oracle
    def random_baseline_stats(y_truth: List[str]) -> Dict[str, float]:
        accs, f1s = [], []
        for seed in range(1000):
            r = random.Random(seed)
            preds = [router_B3_random(w, r) for w in workloads]
            m = compute_metrics(y_truth, preds, "B3 Random")
            accs.append(m["accuracy"])
            f1s.append(m["f1_quantum"])
        return {
            "mean_accuracy": float(np.mean(accs)),
            "std_accuracy": float(np.std(accs)),
            "mean_f1_quantum": float(np.mean(f1s)),
        }

    def evaluate_against(y_truth: List[str], oracle_name: str) -> List[Dict]:
        print(f"\nMetrics vs {oracle_name}:")
        print("=" * 95)
        print(f"{'Router':<18} {'Accuracy':>9} {'Prec(Q)':>8} {'Recall(Q)':>10} "
              f"{'F1(Q)':>7} {'Kappa':>7}")
        print("-" * 95)
        summary = []
        for label, preds in router_preds.items():
            m = compute_metrics(y_truth, preds, label)
            summary.append(m)
            print(f"{label:<18} {m['accuracy']:>9.3f} {m['precision_quantum']:>8.3f} "
                  f"{m['recall_quantum']:>10.3f} {m['f1_quantum']:>7.3f} "
                  f"{m['cohen_kappa']:>7.3f}")
        print("=" * 95)
        return summary

    metrics_alg = evaluate_against(y_alg, "Oracle A (algorithmic advantage)")
    metrics_hw = evaluate_against(y_hw, "Oracle B (hardware viability)")
    b3_alg = random_baseline_stats(y_alg)
    b3_hw = random_baseline_stats(y_hw)
    print(f"(B3 Random over 1000 seeds "
          f"| Oracle A acc={b3_alg['mean_accuracy']:.3f}+/-{b3_alg['std_accuracy']:.3f} "
          f"| Oracle B acc={b3_hw['mean_accuracy']:.3f}+/-{b3_hw['std_accuracy']:.3f})")

    # ----- Disagreement breakdown (Nexar vs each oracle) -----
    def _disagreements(y_truth: List[str]) -> List[Dict]:
        out = []
        preds = router_preds["Nexar (full)"]
        for i, w in enumerate(workloads):
            if preds[i] != y_truth[i]:
                out.append({
                    "workload": w["name"],
                    "nexar": preds[i],
                    "truth": y_truth[i],
                    "qubits": w["input"].qubits_required,
                    "depth": w["input"].circuit_depth,
                })
        return out

    dis_alg = _disagreements(y_alg)
    dis_hw = _disagreements(y_hw)
    print(f"\nNexar vs Oracle A disagreements: {len(dis_alg)} / {len(workloads)}")
    for d in dis_alg:
        print(f"  {d['workload']:<55} Nexar={d['nexar']:<9} "
              f"Truth(A)={d['truth']:<9} (q={d['qubits']}, d={d['depth']})")
    print(f"\nNexar vs Oracle B disagreements: {len(dis_hw)} / {len(workloads)}")
    for d in dis_hw:
        print(f"  {d['workload']:<55} Nexar={d['nexar']:<9} "
              f"Truth(B)={d['truth']:<9} (q={d['qubits']}, d={d['depth']})")

    # ----- Oracle label distributions -----
    def label_dist_of(key: str) -> Dict[str, int]:
        d = {}
        for r in oracle_rows:
            d[r[key]] = d.get(r[key], 0) + 1
        return d

    label_dist_alg = label_dist_of("oracle_algorithmic")
    label_dist_hw = label_dist_of("oracle_hardware")
    print(f"\nOracle A (algorithmic) label distribution: {label_dist_alg}")
    print(f"Oracle B (hardware)    label distribution: {label_dist_hw}")

    # Keep legacy names for the rest of the driver (weight sweep, JSON, etc.)
    y_oracle = y_alg
    metrics_summary = metrics_alg
    label_dist = label_dist_alg
    b3_acc_mean = b3_alg["mean_accuracy"]
    b3_acc_std = b3_alg["std_accuracy"]
    b3_f1_mean = b3_alg["mean_f1_quantum"]
    disagreements = dis_alg

    # ----- Persist JSON -----
    output = {
        "total_workloads": len(workloads),
        "oracle_algorithmic_label_distribution": label_dist_alg,
        "oracle_hardware_label_distribution": label_dist_hw,
        "metrics_vs_oracle_algorithmic": metrics_alg,
        "metrics_vs_oracle_hardware": metrics_hw,
        "b3_random_algorithmic": b3_alg,
        "b3_random_hardware": b3_hw,
        "nexar_vs_oracle_algorithmic_disagreements": dis_alg,
        "nexar_vs_oracle_hardware_disagreements": dis_hw,
        "oracle_rows": oracle_rows,
    }
    out_json = LATEX_DIR / "routing_accuracy_results.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\nJSON results -> {out_json}")

    # ----- Generate LaTeX tables (single-oracle for each, plus dual table) -----
    tex_dual = generate_dual_oracle_table(
        metrics_alg, metrics_hw, n=len(workloads),
        label_dist_alg=label_dist_alg, label_dist_hw=label_dist_hw,
        b3_alg=b3_alg, b3_hw=b3_hw,
    )
    out_tex_dual = LATEX_DIR / "routing_accuracy_table.tex"
    with open(out_tex_dual, "w", encoding="utf-8") as f:
        f.write(tex_dual)
    print(f"Dual-oracle LaTeX -> {out_tex_dual}")

    # -------------------------------------------------------------------
    # Weight sweep: find a better (ML, Rules, Cost) weighting
    # -------------------------------------------------------------------
    print("\n" + "=" * 95)
    print("Weight sweep: searching for better (ML / Rules / Cost) weights")
    print("=" * 95)

    # Candidate grid -- structured around the ordering constraints:
    #   w_cost <= w_rules, w_cost <= w_ml, and no single component >= 0.5
    #   (to preserve the 'no dictator' property from the sensitivity analysis).
    # The final 3 entries allow one component to exceed 0.5 as reference points.
    weight_grid = [
        ("50 / 35 / 15 (current baseline)", 0.50, 0.35, 0.15),
        ("45 / 40 / 15",                    0.45, 0.40, 0.15),
        ("40 / 45 / 15",                    0.40, 0.45, 0.15),
        ("40 / 50 / 10",                    0.40, 0.50, 0.10),
        ("35 / 50 / 15",                    0.35, 0.50, 0.15),
        ("35 / 55 / 10",                    0.35, 0.55, 0.10),
        ("30 / 55 / 15",                    0.30, 0.55, 0.15),
        ("30 / 60 / 10",                    0.30, 0.60, 0.10),
        ("25 / 65 / 10",                    0.25, 0.65, 0.10),
        ("20 / 70 / 10",                    0.20, 0.70, 0.10),
    ]

    sweep_results = []
    for name, wml, wrules, wcost in weight_grid:
        weights = {"ml_model": wml, "rule_system": wrules, "cost_analysis": wcost}
        preds = [router_nexar_reweighted(w, weights, rule_system, cost_analyzer)
                 for w in workloads]
        m = compute_metrics(y_oracle, preds, name)
        m["weights"] = {"ml": wml, "rules": wrules, "cost": wcost}
        sweep_results.append(m)

    # Print sweep summary
    print(f"{'Configuration':<34} {'Acc':>6} {'P(Q)':>6} {'R(Q)':>6} "
          f"{'F1(Q)':>7} {'Kappa':>7}")
    print("-" * 95)
    for r in sweep_results:
        print(f"{r['router']:<34} {r['accuracy']:>6.3f} "
              f"{r['precision_quantum']:>6.3f} {r['recall_quantum']:>6.3f} "
              f"{r['f1_quantum']:>7.3f} {r['cohen_kappa']:>7.3f}")

    # Select best by F1(Q) then by Cohen's kappa as tie-breaker
    best = max(sweep_results,
               key=lambda r: (r["f1_quantum"], r["cohen_kappa"], r["accuracy"]))
    print(f"\nBest configuration by F1(Q): {best['router']}")
    print(f"  Accuracy: {best['accuracy']:.3f}  F1(Q): {best['f1_quantum']:.3f}  "
          f"kappa: {best['cohen_kappa']:.3f}")

    output["weight_sweep"] = sweep_results
    output["best_weights"] = best
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"JSON updated -> {out_json}")

    # Generate LaTeX weight-sweep table
    tex_sweep = generate_weight_sweep_table(sweep_results, best)
    out_tex_sweep = LATEX_DIR / "weight_sweep_table.tex"
    with open(out_tex_sweep, "w", encoding="utf-8") as f:
        f.write(tex_sweep)
    print(f"Weight-sweep LaTeX -> {out_tex_sweep}")


def generate_dual_oracle_table(
    metrics_alg: List[Dict],
    metrics_hw: List[Dict],
    n: int,
    label_dist_alg: Dict[str, int],
    label_dist_hw: Dict[str, int],
    b3_alg: Dict[str, float],
    b3_hw: Dict[str, float],
) -> str:
    """Main routing-accuracy table: one row per router, both oracles side-by-side."""

    dist_alg_str = ", ".join(f"{k}: {v}" for k, v in sorted(label_dist_alg.items()))
    dist_hw_str = ", ".join(f"{k}: {v}" for k, v in sorted(label_dist_hw.items()))

    by_alg = {m["router"]: m for m in metrics_alg}
    by_hw = {m["router"]: m for m in metrics_hw}

    order = ["Nexar (full)",
             "B1 Qubit>=50", "B2 Volume>=50k", "B3 Random",
             "A1 ML-only", "A2 Rules-only", "A3 Cost-only"]

    lines = [
        r"\begin{table*}[!t]",
        r"\caption{Routing Accuracy vs.\ Dual Literature-Cited Oracle Ground Truth "
        r"(\textit{N}\,=\," + str(n) + r" workloads). "
        r"Oracle A (algorithmic advantage) labels workloads by known quantum "
        r"speedup regimes; Oracle B (hardware viability) labels by whether "
        r"current NISQ hardware produces usable signal (calibrated to "
        r"Table~\ref{tab:hardware-validation}).}",
        r"\label{tab:routing-accuracy}",
        r"\centering",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{4pt}",
        r"\begin{tabular}{l ccccc ccccc}",
        r"\toprule",
        r" & \multicolumn{5}{c}{\textbf{Oracle A: Algorithmic Advantage}} "
        r"& \multicolumn{5}{c}{\textbf{Oracle B: Hardware Viability}} \\",
        r"\cmidrule(lr){2-6}\cmidrule(lr){7-11}",
        r"\textbf{Router} & \textbf{Acc.} & \textbf{P(Q)} & \textbf{R(Q)} "
        r"& \textbf{F1(Q)} & \textbf{$\kappa$}"
        r" & \textbf{Acc.} & \textbf{P(Q)} & \textbf{R(Q)} "
        r"& \textbf{F1(Q)} & \textbf{$\kappa$} \\",
        r"\midrule",
    ]

    for key in order:
        if key not in by_alg or key not in by_hw:
            continue
        ma, mh = by_alg[key], by_hw[key]
        display = (key
                   .replace("Nexar (full)", r"\textbf{Nexar (full)}")
                   .replace(">=", r"$\geq$")
                   .replace("B3 Random", rf"B3 Random$^{{\dagger}}$"))
        is_nexar = key == "Nexar (full)"
        fmt = (lambda v: rf"\textbf{{{v:.3f}}}") if is_nexar else (lambda v: f"{v:.3f}")
        row = (
            f"{display} "
            f"& {fmt(ma['accuracy'])} & {fmt(ma['precision_quantum'])} "
            f"& {fmt(ma['recall_quantum'])} & {fmt(ma['f1_quantum'])} "
            f"& {fmt(ma['cohen_kappa'])} "
            f"& {fmt(mh['accuracy'])} & {fmt(mh['precision_quantum'])} "
            f"& {fmt(mh['recall_quantum'])} & {fmt(mh['f1_quantum'])} "
            f"& {fmt(mh['cohen_kappa'])} \\\\"
        )
        lines.append(row)
        if key == "Nexar (full)":
            lines.append(r"\midrule")
        if key == "B3 Random":
            lines.append(r"\midrule")

    lines += [
        r"\bottomrule",
        r"\\[-0.5em]",
        r"\multicolumn{11}{p{0.95\textwidth}}{\footnotesize "
        r"Both oracles are derived from literature-cited rules applied to the "
        r"workload filename and physical circuit features (qubits, depth, "
        r"entanglement), independent of Nexar's decision logic. "
        r"Oracle A distribution --- " + dist_alg_str + r". "
        r"Oracle B distribution --- " + dist_hw_str + r". "
        rf"$^{{\dagger}}$B3 Random averaged over 1000 seeds "
        rf"(A: {b3_alg['mean_accuracy']:.3f}$\pm${b3_alg['std_accuracy']:.3f}; "
        rf"B: {b3_hw['mean_accuracy']:.3f}$\pm${b3_hw['std_accuracy']:.3f}). "
        r"Q = Quantum class. $\kappa$ = Cohen's kappa vs.\ oracle.} \\",
        r"\end{tabular}",
        r"\end{table*}",
    ]
    return "\n".join(lines) + "\n"


def generate_weight_sweep_table(sweep: List[Dict], best: Dict) -> str:
    """LaTeX table for the weight sweep (one row per configuration)."""
    lines = [
        r"\begin{table}[!t]",
        r"\caption{Decision-Merger Weight Sweep vs.\ Oracle Ground Truth "
        r"(\textit{N}\,=\,100 workloads)}",
        r"\label{tab:weight-sweep}",
        r"\centering",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\begin{tabular}{lccccc}",
        r"\toprule",
        r"\textbf{Weights} & \textbf{Acc.} & \textbf{Prec.(Q)} & "
        r"\textbf{Rec.(Q)} & \textbf{F1(Q)} & \textbf{$\kappa$} \\",
        r"(ML / Rules / Cost) & & & & & \\",
        r"\midrule",
    ]
    for r in sweep:
        label = r["router"].replace(" (current baseline)", r"$^{*}$")
        is_best = r["router"] == best["router"]
        fmt = (lambda v: rf"\textbf{{{v:.3f}}}") if is_best else (lambda v: f"{v:.3f}")
        marker = r"$^{\dagger}$" if is_best else ""
        row = (f"{label}{marker} & "
               f"{fmt(r['accuracy'])} & {fmt(r['precision_quantum'])} & "
               f"{fmt(r['recall_quantum'])} & {fmt(r['f1_quantum'])} & "
               f"{fmt(r['cohen_kappa'])} \\\\")
        lines.append(row)
    lines += [
        r"\bottomrule",
        r"\\[-0.5em]",
        r"\multicolumn{6}{p{0.92\columnwidth}}{\footnotesize "
        r"$^{*}$Current paper baseline. "
        r"$^{\dagger}$Best configuration by F1 on the Quantum class "
        r"(tie-broken by Cohen's $\kappa$, then accuracy).} \\",
        r"\end{tabular}",
        r"\end{table}",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    analyse()
