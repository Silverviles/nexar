"""
Weight Sensitivity Analysis for Nexar Decision Engine
======================================================
Tests how routing decisions change across 6 weight configurations
against all 100 benchmark workloads from the paper's evaluation suite.

Usage:
    cd decision-engine
    python scripts/weight_sensitivity_analysis.py

Output:
    - Console table of results
    - latex/weight_sensitivity_results.json  (raw data)
    - latex/weight_sensitivity_table.tex     (LaTeX table for paper)
"""

import sys
import os
import csv
import json
import copy

# ---------------------------------------------------------------------------
# Path setup — run from decision-engine/ directory
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.rule_service import RuleBasedSystem, RuleDecisionType
from services.cost_analyser import CostAnalyzer
from services.decision_merger import DecisionMerger
from schemas.decision_engine import (
    CodeAnalysisInput,
    HardwareType,
    ProblemType,
    TimeComplexity,
)

# ---------------------------------------------------------------------------
# Weight configurations to test
# ---------------------------------------------------------------------------
WEIGHT_CONFIGS = [
    ("Baseline (50/35/15)",     {"ml_model": 0.50, "rule_system": 0.35, "cost_analysis": 0.15}),
    ("ML-Heavy (70/20/10)",     {"ml_model": 0.70, "rule_system": 0.20, "cost_analysis": 0.10}),
    ("Rule-Heavy (30/55/15)",   {"ml_model": 0.30, "rule_system": 0.55, "cost_analysis": 0.15}),
    ("Equal (33/33/34)",        {"ml_model": 0.33, "rule_system": 0.33, "cost_analysis": 0.34}),
    ("Cost-Sensitive (40/30/30)", {"ml_model": 0.40, "rule_system": 0.30, "cost_analysis": 0.30}),
    ("ML-Only (100/0/0)",       {"ml_model": 1.00, "rule_system": 0.00, "cost_analysis": 0.00}),
]

# ---------------------------------------------------------------------------
# Enum mappings
# ---------------------------------------------------------------------------
PROBLEM_TYPE_MAP = {
    "factorization":    ProblemType.FACTORIZATION,
    "search":           ProblemType.SEARCH,
    "simulation":       ProblemType.SIMULATION,
    "optimization":     ProblemType.OPTIMIZATION,
    "sorting":          ProblemType.SORTING,
    "dynamic_programming": ProblemType.DYNAMIC_PROGRAMMING,
    "matrix_ops":       ProblemType.MATRIX_OPS,
    "random_circuit":   ProblemType.RANDOM_CIRCUIT,
    "sampling":         ProblemType.SAMPLING,
}

TIME_COMPLEXITY_MAP = {
    "polynomial":         TimeComplexity.POLYNOMIAL,
    "exponential":        TimeComplexity.EXPONENTIAL,
    "quadratic_speedup":  TimeComplexity.QUADRATIC_SPEEDUP,
    "polynomial_speedup": TimeComplexity.POLYNOMIAL_SPEEDUP,
    "nlogn":              TimeComplexity.NLOGN,
}


def load_workloads(csv_path: str) -> list:
    """Load all 100 workloads from the benchmark CSV."""
    workloads = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("status") != "completed":
                continue

            # Map problem type (use mapped_problem_type, fall back to raw)
            pt_str = row.get("mapped_problem_type") or row.get("problem_type", "sorting")
            pt = PROBLEM_TYPE_MAP.get(pt_str.lower(), ProblemType.SORTING)

            # Map time complexity (use mapped_time_complexity, fall back to raw)
            tc_str = row.get("mapped_time_complexity") or row.get("time_complexity", "polynomial")
            # Normalise O(...) notation if present
            tc_str = (tc_str.lower()
                      .replace("o(n^2)", "quadratic_speedup")
                      .replace("o(n log n)", "nlogn")
                      .replace("o(n)", "polynomial")
                      .replace("o(2^n)", "exponential"))
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
            except Exception as e:
                print(f"  [WARN] Skipping {row['workload_name']}: {e}")
                continue

            workloads.append({
                "name": row["workload_name"],
                "input": inp,
                "baseline_hw": row["recommended_hardware"],
                "ml_quantum_prob": float(row["quantum_probability"]),
                "ml_classical_prob": float(row["classical_probability"]),
                "baseline_rationale": row["rationale"],
            })
    return workloads


def run_with_weights(
    workload: dict,
    weights: dict,
    rule_system: RuleBasedSystem,
    cost_analyzer: CostAnalyzer,
) -> str:
    """Return routing decision ('Quantum' or 'Classical') for one weight config."""

    inp = workload["input"]
    q_prob = workload["ml_quantum_prob"]
    c_prob = workload["ml_classical_prob"]

    # 1. Reconstruct ML decision
    ml_hw = HardwareType.QUANTUM if q_prob >= c_prob else HardwareType.CLASSICAL
    ml_confidence = max(q_prob, c_prob)
    ml_decision = {
        "hardware": ml_hw,
        "confidence": ml_confidence,
        "quantum_probability": q_prob,
        "classical_probability": c_prob,
        "rationale": f"ML: {ml_hw.value} @ {ml_confidence:.1%}",
    }

    # 2. Rule evaluation
    rule_decision = rule_system.evaluate(inp)

    # 3. Cost analysis (uses ML hardware suggestion)
    cost_analysis = cost_analyzer.analyze(inp, ml_hw, budget_limit_usd=None)

    # 4. Decision merger with patched weights
    merger = DecisionMerger()
    merger.decision_weights = dict(weights)  # patch weights

    rec = merger.merge(ml_decision, rule_decision, cost_analysis)
    return rec.recommended_hardware.value


def analyse(csv_path: str):
    """Run the full sensitivity sweep and print results."""

    print("Loading workloads from", csv_path)
    workloads = load_workloads(csv_path)
    print(f"Loaded {len(workloads)} workloads")

    rule_system = RuleBasedSystem()
    cost_analyzer = CostAnalyzer()

    # -------------------------------------------------------------------
    # First pass: establish baseline using the paper's 50/35/15 weights
    # -------------------------------------------------------------------
    baseline_name, baseline_weights = WEIGHT_CONFIGS[0]
    baseline_results = {}
    for w in workloads:
        hw = run_with_weights(w, baseline_weights, rule_system, cost_analyzer)
        baseline_results[w["name"]] = hw

    baseline_quantum = sum(1 for v in baseline_results.values() if v == "Quantum")
    baseline_classical = len(workloads) - baseline_quantum

    print(f"\nBaseline ({baseline_name}): {baseline_quantum} Quantum / {baseline_classical} Classical")

    # -------------------------------------------------------------------
    # Second pass: all 6 configurations
    # -------------------------------------------------------------------
    config_results = []
    changed_workloads_per_config = {}

    for config_name, weights in WEIGHT_CONFIGS:
        quantum_count = 0
        classical_count = 0
        rule_override_count = 0
        allow_both_count = 0
        changed = []

        for w in workloads:
            # Track rule override vs weighted path
            inp = w["input"]
            rule_dec = rule_system.evaluate(inp)
            if rule_dec["decision_type"] in (
                RuleDecisionType.FORCE_QUANTUM,
                RuleDecisionType.FORCE_CLASSICAL,
                RuleDecisionType.REJECT,
            ):
                rule_override_count += 1
            else:
                allow_both_count += 1

            hw = run_with_weights(w, weights, rule_system, cost_analyzer)

            if hw == "Quantum":
                quantum_count += 1
            else:
                classical_count += 1

            if hw != baseline_results[w["name"]]:
                changed.append(w["name"])

        changed_workloads_per_config[config_name] = changed
        config_results.append({
            "config": config_name,
            "weights": weights,
            "quantum": quantum_count,
            "classical": classical_count,
            "rule_overrides": rule_override_count,
            "allow_both": allow_both_count,
            "changed_vs_baseline": len(changed),
            "changed_workloads": changed,
        })

    # -------------------------------------------------------------------
    # Print console summary
    # -------------------------------------------------------------------
    print()
    print("=" * 90)
    print(f"{'Weight Configuration':<30} {'Quantum':>8} {'Classical':>9} {'Changed':>8} {'Rule Override':>14} {'Weighted':>9}")
    print("=" * 90)
    for r in config_results:
        marker = " <-- baseline" if r["config"] == baseline_name else ""
        print(
            f"{r['config']:<30} {r['quantum']:>8} {r['classical']:>9} "
            f"{r['changed_vs_baseline']:>8} {r['rule_overrides']:>14} {r['allow_both']:>9}"
            + marker
        )
    print("=" * 90)

    # Show which workloads changed in any config
    all_changed = set()
    for r in config_results:
        all_changed.update(r["changed_workloads"])

    if all_changed:
        print(f"\nWorkloads that changed routing in at least one configuration ({len(all_changed)}):")
        for name in sorted(all_changed):
            w = next(x for x in workloads if x["name"] == name)
            baseline_hw = baseline_results[name]
            configs_flipped = [r["config"] for r in config_results if name in r["changed_workloads"]]
            print(f"  {name}")
            print(f"    Baseline: {baseline_hw} | q_prob={w['ml_quantum_prob']:.4f}")
            print(f"    Flipped in: {', '.join(configs_flipped)}")
            inp = w["input"]
            rule_dec = rule_system.evaluate(inp)
            print(f"    Rule path: {rule_dec['decision_type']}")
    else:
        print("\nNo workloads changed routing under any weight configuration tested.")

    # -------------------------------------------------------------------
    # Compute decision margin for ALLOW_BOTH workloads
    # -------------------------------------------------------------------
    margins = []
    for w in workloads:
        inp = w["input"]
        rule_dec = rule_system.evaluate(inp)
        if rule_dec["decision_type"] == RuleDecisionType.ALLOW_BOTH:
            q_prob = w["ml_quantum_prob"]
            c_prob = w["ml_classical_prob"]
            ml_hw = HardwareType.QUANTUM if q_prob >= c_prob else HardwareType.CLASSICAL
            cost_analysis = cost_analyzer.analyze(inp, ml_hw, budget_limit_usd=None)

            # Simulate baseline scoring
            merger = DecisionMerger()
            ml_confidence = max(q_prob, c_prob)
            scores = merger._calculate_decision_scores(
                ml_hw, ml_confidence,
                rule_dec.get("hardware"), rule_dec.get("confidence", 0.5),
                HardwareType(cost_analysis["cost_optimal_hardware"]),
                cost_analysis["cost_agrees_with_ml"],
            )
            q_score = scores["Quantum"]["total_score"]
            c_score = scores["Classical"]["total_score"]
            margin = abs(q_score - c_score)
            margins.append({
                "name": w["name"],
                "baseline_hw": baseline_results[w["name"]],
                "q_score": q_score,
                "c_score": c_score,
                "margin": margin,
            })

    print(f"\nALLOW_BOTH path workloads ({len(margins)} total):")
    print(f"{'Workload':<50} {'Decision':>10} {'Q-score':>8} {'C-score':>8} {'Margin':>8}")
    print("-" * 90)
    for m in sorted(margins, key=lambda x: x["margin"]):
        print(f"{m['name']:<50} {m['baseline_hw']:>10} {m['q_score']:>8.4f} {m['c_score']:>8.4f} {m['margin']:>8.4f}")

    avg_margin = sum(m["margin"] for m in margins) / len(margins) if margins else 0
    min_margin = min(m["margin"] for m in margins) if margins else 0
    print(f"\n  Average margin: {avg_margin:.4f}  |  Minimum margin: {min_margin:.4f}")

    # -------------------------------------------------------------------
    # Write results JSON
    # -------------------------------------------------------------------
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "..", "latex")
    out_json = os.path.join(out_dir, "weight_sensitivity_results.json")

    output = {
        "total_workloads": len(workloads),
        "baseline": baseline_name,
        "baseline_quantum": baseline_quantum,
        "baseline_classical": baseline_classical,
        "configs": config_results,
        "allow_both_margins": margins,
    }
    # Remove non-serialisable keys
    for c in output["configs"]:
        c["weights"] = {k: round(v, 4) for k, v in c["weights"].items()}

    with open(out_json, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {out_json}")

    # -------------------------------------------------------------------
    # Generate LaTeX table
    # -------------------------------------------------------------------
    tex = generate_latex_table(config_results, len(workloads), baseline_name)
    out_tex = os.path.join(out_dir, "weight_sensitivity_table.tex")
    with open(out_tex, "w") as f:
        f.write(tex)
    print(f"LaTeX table saved to {out_tex}")

    return output


def generate_latex_table(config_results: list, total: int, baseline_name: str) -> str:
    """Generate the LaTeX table for the paper."""

    lines = [
        r"\begin{table}[!t]",
        r"\caption{Weight Sensitivity Analysis: Routing Stability Across Six Weight Configurations (\textit{N}\,=\,100 workloads)}",
        r"\label{tab:weight-sensitivity}",
        r"\centering",
        r"\setlength{\tabcolsep}{4pt}",
        r"\begin{tabular}{lcccc}",
        r"\toprule",
        r"\textbf{Weight Configuration} & \textbf{Quantum} & \textbf{Classical} & \textbf{Changed} & \textbf{Weighted Path} \\",
        r"(ML / Rules / Cost) & \textbf{Routed} & \textbf{Routed} & \textbf{vs.\ Baseline} & \textbf{Workloads} \\",
        r"\midrule",
    ]

    for r in config_results:
        # Extract weight percentages from config name
        name = r["config"]
        is_baseline = (name == baseline_name)

        # Format as "50 / 35 / 15"
        w = r["weights"]
        ml_pct = int(round(w["ml_model"] * 100))
        rule_pct = int(round(w["rule_system"] * 100))
        cost_pct = int(round(w["cost_analysis"] * 100))
        config_label = f"{ml_pct} / {rule_pct} / {cost_pct}"

        changed = r["changed_vs_baseline"]
        changed_str = r"--" if changed == 0 else str(changed)

        # Mark baseline row
        if is_baseline:
            row = (
                rf"\textbf{{{config_label}}} (baseline) & \textbf{{{r['quantum']}}} & "
                rf"\textbf{{{r['classical']}}} & {changed_str} & {r['allow_both']} \\"
            )
        else:
            pct_stable = 100.0 * (total - changed) / total
            row = (
                rf"{config_label} & {r['quantum']} & {r['classical']} & "
                rf"{changed_str} ({pct_stable:.0f}\%\ stable) & {r['allow_both']} \\"
            )
        lines.append(row)

    rule_override_count = config_results[0]["rule_overrides"]
    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\vspace{2pt}",
        (
            r"\begin{minipage}{\linewidth}"
            r"\footnotesize"
            r"\textit{Changed vs.\ Baseline}: number of workloads whose routing decision differs from the "
            r"50/35/15 baseline. \textit{Weighted Path}: workloads that reach the weighted-merger stage "
            r"(rule overrides, applied to " + str(rule_override_count) + r" workloads, bypass weights entirely). "
            r"A dash (--) indicates the baseline itself."
            r"\end{minipage}"
        ),
        r"\end{table}",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "..", "benchmarks", "results", "pipeline_dataset.csv"
    )
    if not os.path.exists(csv_path):
        print(f"ERROR: CSV not found at {csv_path}")
        sys.exit(1)

    analyse(csv_path)
