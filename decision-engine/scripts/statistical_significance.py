"""Statistical robustness analysis for C3 reviewer concern.

Produces:
  1. Paired bootstrap 95% CIs for F1(Q) and Cohen's kappa for every router
     against both oracles (2,000 resamples with replacement over the 100
     workloads, preserving the (y_true, y_pred) pairing).
  2. Pairwise McNemar tests for Nexar (full) vs each of the 6 baselines and
     ablations, both oracles. Uses the exact binomial McNemar when the
     discordant-pair count b+c < 25, else the asymptotic chi-square.

Outputs:
    latex/statistical_significance_table.tex
    latex/statistical_significance.json
"""
from __future__ import annotations

import importlib.util
import json
import random
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from scipy.stats import binomtest, chi2
from sklearn.metrics import cohen_kappa_score, precision_recall_fscore_support

SCRIPT_DIR = Path(__file__).resolve().parent
ENGINE_DIR = SCRIPT_DIR.parent
REPO_ROOT = ENGINE_DIR.parent
sys.path.insert(0, str(ENGINE_DIR))
sys.path.insert(0, str(SCRIPT_DIR))

# Reuse routing_accuracy_analysis.py wholesale
spec = importlib.util.spec_from_file_location(
    "raa", SCRIPT_DIR / "routing_accuracy_analysis.py"
)
raa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(raa)

from services.cost_analyser import CostAnalyzer
from services.rule_service import RuleBasedSystem

CSV_PATH = REPO_ROOT / "benchmarks" / "results" / "pipeline_dataset.csv"
LATEX_DIR = REPO_ROOT / "latex"
N_BOOTSTRAP = 2000
SEED = 20260419


def f1_quantum(y_true: List[str], y_pred: List[str]) -> float:
    yt = [1 if x == "Quantum" else 0 for x in y_true]
    yp = [1 if x == "Quantum" else 0 for x in y_pred]
    _, _, f1, _ = precision_recall_fscore_support(
        yt, yp, average="binary", zero_division=0
    )
    return float(f1)


def kappa(y_true: List[str], y_pred: List[str]) -> float:
    return float(cohen_kappa_score(
        y_true, y_pred, labels=["Classical", "Quantum", "Reject"]
    ))


def bootstrap_ci(
    y_true: List[str],
    y_pred: List[str],
    stat_fn,
    n_resamples: int = N_BOOTSTRAP,
    seed: int = SEED,
) -> Tuple[float, float, float]:
    """Paired bootstrap: resample the 100 (y_true, y_pred) pairs with
    replacement; return (point_estimate, ci_low, ci_high) at 95% percentile.
    """
    rng = np.random.default_rng(seed)
    n = len(y_true)
    point = stat_fn(y_true, y_pred)
    estimates = np.empty(n_resamples, dtype=float)
    for i in range(n_resamples):
        idx = rng.integers(0, n, size=n)
        yt = [y_true[j] for j in idx]
        yp = [y_pred[j] for j in idx]
        estimates[i] = stat_fn(yt, yp)
    # Degenerate resamples (single-class bootstrap draws) give NaN for kappa;
    # drop them before taking percentiles so the CI reflects the well-defined
    # resamples only. If too few survive, fall back to the point estimate.
    finite = estimates[np.isfinite(estimates)]
    if len(finite) < 20:
        return point, point, point
    lo = float(np.percentile(finite, 2.5))
    hi = float(np.percentile(finite, 97.5))
    return point, lo, hi


def mcnemar_p(y_true: List[str], y_nexar: List[str], y_other: List[str]
              ) -> Dict[str, float]:
    """McNemar test on paired correctness vs the oracle.

    b = Nexar wrong, Other correct
    c = Nexar correct, Other wrong
    """
    b = 0
    c = 0
    for t, n, o in zip(y_true, y_nexar, y_other):
        n_ok = (n == t)
        o_ok = (o == t)
        if (not n_ok) and o_ok:
            b += 1
        elif n_ok and (not o_ok):
            c += 1
    n_disc = b + c
    if n_disc == 0:
        return {"b": b, "c": c, "n_disc": 0, "p_value": 1.0, "method": "identical"}
    if n_disc < 25:
        # Exact McNemar: binomial on b / (b+c) with p=0.5, two-sided
        res = binomtest(b, n_disc, p=0.5, alternative="two-sided")
        return {"b": b, "c": c, "n_disc": n_disc,
                "p_value": float(res.pvalue), "method": "exact"}
    # Asymptotic McNemar with continuity correction
    stat = (abs(b - c) - 1) ** 2 / n_disc
    p = float(1 - chi2.cdf(stat, df=1))
    return {"b": b, "c": c, "n_disc": n_disc, "p_value": p, "method": "chi2"}


def main() -> None:
    print(f"Loading workloads from {CSV_PATH}")
    workloads = raa.load_workloads(CSV_PATH)
    print(f"Loaded {len(workloads)} workloads")

    rule_system = RuleBasedSystem()
    cost_analyzer = CostAnalyzer()
    rng = random.Random(42)

    # Generate predictions once per router (match routing_accuracy_analysis.py)
    preds: Dict[str, List[str]] = {
        "Nexar (full)":     [raa.router_nexar_live(w, rule_system, cost_analyzer)
                             for w in workloads],
        "B1 Qubit>=50":     [raa.router_B1_qubit_threshold(w)          for w in workloads],
        "B2 Volume>=50k":   [raa.router_B2_volume_threshold(w)         for w in workloads],
        "B3 Random":        [raa.router_B3_random(w, rng)              for w in workloads],
        "A1 ML-only":       [raa.router_A1_ml_only(w)                  for w in workloads],
        "A2 Rules-only":    [raa.router_A2_rules_only(w, rule_system)  for w in workloads],
        "A3 Cost-only":     [raa.router_A3_cost_only(w, cost_analyzer) for w in workloads],
    }

    # Oracle labels
    y_alg, y_hw = [], []
    for w in workloads:
        inp = w["input"]
        la, _ = raa.oracle_algorithmic(
            w["name"], inp.qubits_required, inp.circuit_depth, inp.entanglement_score
        )
        lb, _ = raa.oracle_hardware_viability(
            w["name"], inp.qubits_required, inp.circuit_depth, inp.entanglement_score
        )
        y_alg.append(la)
        y_hw.append(lb)

    router_order = list(preds.keys())
    results: Dict[str, dict] = {"routers": {}}

    for router in router_order:
        yp = preds[router]
        row = {}
        for oracle_key, y_true in [("oracle_a", y_alg), ("oracle_b", y_hw)]:
            f1, f1_lo, f1_hi = bootstrap_ci(y_true, yp, f1_quantum)
            k, k_lo, k_hi = bootstrap_ci(y_true, yp, kappa)
            row[oracle_key] = {
                "f1_q": f1, "f1_q_ci": [f1_lo, f1_hi],
                "kappa": k, "kappa_ci": [k_lo, k_hi],
            }
        results["routers"][router] = row

    # McNemar: Nexar (full) vs each of the 6 others, both oracles
    y_nexar = preds["Nexar (full)"]
    mcnemar_rows: Dict[str, dict] = {}
    for router in router_order:
        if router == "Nexar (full)":
            continue
        mcnemar_rows[router] = {
            "oracle_a": mcnemar_p(y_alg, y_nexar, preds[router]),
            "oracle_b": mcnemar_p(y_hw, y_nexar, preds[router]),
        }
    results["mcnemar_vs_nexar"] = mcnemar_rows

    # Persist JSON
    out_json = LATEX_DIR / "statistical_significance.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"JSON -> {out_json}")

    # Pretty print
    print("\nBootstrap 95% CIs (n=2,000 paired resamples)")
    print("=" * 95)
    print(f"{'Router':<18} {'F1(Q)-A':>10} {'CI-A':>18} {'F1(Q)-B':>10} {'CI-B':>18}")
    print("-" * 95)
    for r in router_order:
        a = results["routers"][r]["oracle_a"]
        b = results["routers"][r]["oracle_b"]
        print(f"{r:<18} {a['f1_q']:>10.3f} "
              f"[{a['f1_q_ci'][0]:.3f}, {a['f1_q_ci'][1]:.3f}]   "
              f"{b['f1_q']:>10.3f} "
              f"[{b['f1_q_ci'][0]:.3f}, {b['f1_q_ci'][1]:.3f}]")
    print("=" * 95)

    print("\nMcNemar Nexar (full) vs each other router (paired correctness)")
    print("=" * 95)
    print(f"{'Comparison':<28} {'Oracle A (b/c, p)':>28} {'Oracle B (b/c, p)':>28}")
    print("-" * 95)
    for r in router_order:
        if r == "Nexar (full)":
            continue
        a = mcnemar_rows[r]["oracle_a"]
        b = mcnemar_rows[r]["oracle_b"]
        label = f"Nexar vs {r}"
        print(f"{label:<28} {a['b']}/{a['c']} p={a['p_value']:.4f} ({a['method']:<5}) "
              f"  {b['b']}/{b['c']} p={b['p_value']:.4f} ({b['method']})")
    print("=" * 95)

    # Generate LaTeX
    tex = generate_table(results, router_order)
    out_tex = LATEX_DIR / "statistical_significance_table.tex"
    with open(out_tex, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"LaTeX -> {out_tex}")


def _fmt_ci(ci: List[float]) -> str:
    return rf"[{ci[0]:.2f},\,{ci[1]:.2f}]"


def _fmt_p(p: float) -> str:
    """Return the relation + value so the caller wraps with $p{_fmt_p(...)}$."""
    if p < 0.001:
        return "{<}0.001"
    if p < 0.01:
        return f"{{=}}{p:.3f}"
    return f"{{=}}{p:.2f}"


def generate_table(results: dict, router_order: List[str]) -> str:
    routers_data = results["routers"]
    mcnemar = results["mcnemar_vs_nexar"]

    lines = [
        r"\begin{table}[!t]",
        r"\caption{Statistical Robustness of Routing Metrics. Bootstrap 95\% "
        r"CIs (2{,}000 paired resamples of the 100 workloads, preserving "
        r"$(y_\text{true}, y_\text{pred})$ pairing). McNemar tests compare "
        r"Nexar (full) against each baseline/ablation on paired correctness "
        r"(exact binomial when discordant pairs $<$25).}",
        r"\label{tab:statistical-significance}",
        r"\centering",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\begin{tabular}{l cc cc}",
        r"\toprule",
        r" & \multicolumn{2}{c}{\textbf{Oracle A}} & "
        r"\multicolumn{2}{c}{\textbf{Oracle B}} \\",
        r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}",
        r"\textbf{Router} & \textbf{F1(Q) [95\% CI]} & "
        r"\textbf{$\kappa$ [95\% CI]} & "
        r"\textbf{F1(Q) [95\% CI]} & \textbf{$\kappa$ [95\% CI]} \\",
        r"\midrule",
    ]
    for r in router_order:
        a = routers_data[r]["oracle_a"]
        b = routers_data[r]["oracle_b"]
        display = (r.replace(">=", r"$\geq$")
                    .replace("Nexar (full)", r"\textbf{Nexar (full)}"))
        is_nexar = r == "Nexar (full)"
        fmt = (lambda v: rf"\textbf{{{v:.2f}}}") if is_nexar else (lambda v: f"{v:.2f}")
        row = (
            f"{display} & "
            f"{fmt(a['f1_q'])}\\,{_fmt_ci(a['f1_q_ci'])} & "
            f"{fmt(a['kappa'])}\\,{_fmt_ci(a['kappa_ci'])} & "
            f"{fmt(b['f1_q'])}\\,{_fmt_ci(b['f1_q_ci'])} & "
            f"{fmt(b['kappa'])}\\,{_fmt_ci(b['kappa_ci'])} \\\\"
        )
        lines.append(row)
        if r == "Nexar (full)":
            lines.append(r"\midrule")

    lines += [
        r"\midrule",
        r"\multicolumn{5}{l}{\textit{McNemar paired-correctness vs.\ Nexar "
        r"(full): $b$/$c$ discordant, $p$}} \\",
    ]
    for r in router_order:
        if r == "Nexar (full)":
            continue
        a = mcnemar[r]["oracle_a"]
        b = mcnemar[r]["oracle_b"]
        display = r.replace(">=", r"$\geq$")
        lines.append(
            rf"\quad vs.\ {display} & "
            rf"\multicolumn{{2}}{{l}}{{A: {a['b']}/{a['c']}, "
            rf"$p{_fmt_p(a['p_value'])}$}} & "
            rf"\multicolumn{{2}}{{l}}{{B: {b['b']}/{b['c']}, "
            rf"$p{_fmt_p(b['p_value'])}$}} \\"
        )

    lines += [
        r"\bottomrule",
        r"\\[-0.5em]",
        r"\multicolumn{5}{p{0.92\columnwidth}}{\footnotesize "
        r"Quantum-class positives are few (14 under Oracle~A, 7 under "
        r"Oracle~B), so F1(Q) CIs are intrinsically wide; the McNemar test "
        r"on paired correctness is the more powerful significance probe "
        r"because it conditions on discordant pairs only. $b$ = Nexar "
        r"wrong, other correct; $c$ = Nexar correct, other wrong.} \\",
        r"\end{tabular}",
        r"\end{table}",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
