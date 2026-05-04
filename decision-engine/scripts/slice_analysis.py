"""Slice analysis to decide paper revision path for reviewer's C1 concern.

Re-runs every router from routing_accuracy_analysis.py on sub-slices of the
100-workload benchmark:
    - All 100                    (sanity-check baseline metrics)
    - 39 merger-resolved         (rules emit ALLOW_BOTH; ensemble voting actually fires)
    - 61 rule-overridden         (rules emit FORCE_*/REJECT; all routers trivially agree)
    - 10-30 qubit band           (the regime the reviewer flagged as ML-weak)
    - Nexar quantum-routed 20    (where Nexar commits to quantum)

Emits per-slice accuracy / precision(Q) / recall(Q) / F1(Q) / kappa for:
    Nexar (full), B1, B2, A1 ML-only, A2 Rules-only, A3 Cost-only

Output: latex/slice_analysis_results.json + stdout summary table.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ENGINE_DIR = SCRIPT_DIR.parent
REPO_ROOT = ENGINE_DIR.parent
sys.path.insert(0, str(ENGINE_DIR))
sys.path.insert(0, str(SCRIPT_DIR))

# Import all the machinery from the existing script
import importlib.util
spec = importlib.util.spec_from_file_location("raa", SCRIPT_DIR / "routing_accuracy_analysis.py")
raa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(raa)

from services.cost_analyser import CostAnalyzer
from services.rule_service import RuleBasedSystem, RuleDecisionType

CSV_PATH = REPO_ROOT / "benchmarks" / "results" / "pipeline_dataset.csv"
OUT_PATH = REPO_ROOT / "latex" / "slice_analysis_results.json"


def main():
    print("Loading workloads...")
    workloads = raa.load_workloads(CSV_PATH)
    print(f"Loaded {len(workloads)} workloads\n")

    rule_system = RuleBasedSystem()
    cost_analyzer = CostAnalyzer()
    rng = random.Random(42)

    # Run every router once, capturing per-workload predictions
    preds = {}
    preds["Nexar (full)"] = [raa.router_nexar_live(w, rule_system, cost_analyzer) for w in workloads]
    preds["B1 Qubit>=50"] = [raa.router_B1_qubit_threshold(w) for w in workloads]
    preds["B2 Volume>=50k"] = [raa.router_B2_volume_threshold(w) for w in workloads]
    preds["A1 ML-only"] = [raa.router_A1_ml_only(w) for w in workloads]
    preds["A2 Rules-only"] = [raa.router_A2_rules_only(w, rule_system) for w in workloads]
    preds["A3 Cost-only"] = [raa.router_A3_cost_only(w, cost_analyzer) for w in workloads]

    # Also capture which rule-decision-type each workload gets (for slicing)
    rule_types = []
    for w in workloads:
        dec = rule_system.evaluate(w["input"])
        rule_types.append(dec["decision_type"].name)

    # Oracle ground truth
    labels_a, labels_b = [], []
    for w in workloads:
        inp = w["input"]
        la, _ = raa.oracle_algorithmic(
            w["name"], inp.qubits_required, inp.circuit_depth, inp.entanglement_score
        )
        lb, _ = raa.oracle_hardware_viability(
            w["name"], inp.qubits_required, inp.circuit_depth, inp.entanglement_score
        )
        labels_a.append(la)
        labels_b.append(lb)

    # Build slices as index sets
    def idx(pred):
        return [i for i, w in enumerate(workloads) if pred(i, w)]

    slices = {
        "All (100)": idx(lambda i, w: True),
        "Merger-resolved (ALLOW_BOTH)": idx(lambda i, w: rule_types[i] == "ALLOW_BOTH"),
        "Rule-overridden (FORCE_*/REJECT)": idx(
            lambda i, w: rule_types[i] != "ALLOW_BOTH"
        ),
        "10-30 qubit band": idx(
            lambda i, w: 10 <= w["input"].qubits_required <= 30
        ),
        "Nexar quantum-routed": idx(lambda i, w: preds["Nexar (full)"][i] == "Quantum"),
        "Sub-50 qubit (non-zero)": idx(
            lambda i, w: 1 <= w["input"].qubits_required < 50
        ),
    }

    print(f"Slice sizes: {[(k, len(v)) for k, v in slices.items()]}\n")

    # Compute metrics per slice per router per oracle
    results = {"slices": {}}
    for slice_name, indices in slices.items():
        if not indices:
            continue
        results["slices"][slice_name] = {"size": len(indices), "routers": {}}
        for router in preds:
            yp = [preds[router][i] for i in indices]
            ya = [labels_a[i] for i in indices]
            yb = [labels_b[i] for i in indices]
            ma = raa.compute_metrics(ya, yp, router)
            mb = raa.compute_metrics(yb, yp, router)
            results["slices"][slice_name]["routers"][router] = {
                "oracle_a": {
                    "accuracy": ma["accuracy"],
                    "precision_q": ma["precision_quantum"],
                    "recall_q": ma["recall_quantum"],
                    "f1_q": ma["f1_quantum"],
                    "kappa": ma["cohen_kappa"],
                    "n_pred_quantum": yp.count("Quantum"),
                    "n_true_quantum": ya.count("Quantum"),
                },
                "oracle_b": {
                    "accuracy": mb["accuracy"],
                    "precision_q": mb["precision_quantum"],
                    "recall_q": mb["recall_quantum"],
                    "f1_q": mb["f1_quantum"],
                    "kappa": mb["cohen_kappa"],
                    "n_pred_quantum": yp.count("Quantum"),
                    "n_true_quantum": yb.count("Quantum"),
                },
            }

    # Dump rule-type distribution
    rt_dist = {}
    for rt in rule_types:
        rt_dist[rt] = rt_dist.get(rt, 0) + 1
    results["rule_type_distribution"] = rt_dist

    # Per-workload dump for spot-checks
    results["per_workload"] = []
    for i, w in enumerate(workloads):
        results["per_workload"].append({
            "name": w["name"],
            "qubits": w["input"].qubits_required,
            "depth": w["input"].circuit_depth,
            "rule_type": rule_types[i],
            "oracle_a": labels_a[i],
            "oracle_b": labels_b[i],
            "nexar": preds["Nexar (full)"][i],
            "a2_rules": preds["A2 Rules-only"][i],
            "a1_ml": preds["A1 ML-only"][i],
            "b1_qubit": preds["B1 Qubit>=50"][i],
        })

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Wrote {OUT_PATH}")

    # Pretty print key tables
    print("\n" + "=" * 100)
    print("SLICE SUMMARY: F1(Q) vs Oracle A / Oracle B")
    print("=" * 100)
    routers = ["Nexar (full)", "A2 Rules-only", "A1 ML-only", "B1 Qubit>=50", "B2 Volume>=50k"]
    header = f"{'Slice':<40s}" + "  ".join(f"{r:>15s}" for r in routers)
    print(header)
    for slice_name, sdata in results["slices"].items():
        size = sdata["size"]
        for oracle_key, oname in [("oracle_a", "A"), ("oracle_b", "B")]:
            row = f"{slice_name[:37]:<40s}"
            for r in routers:
                m = sdata["routers"][r][oracle_key]
                row += f"  F1(Q)={m['f1_q']:.3f}/acc={m['accuracy']:.2f}"[:17].rjust(17)
            print(f"[n={size:3d}, {oname}] {row}")
        print()


if __name__ == "__main__":
    main()
