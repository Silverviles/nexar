"""Tier-attribution analysis for the three-tier algorithm classifier (C6).

Replicates the tier-selection logic in `main.py::analyze_code` and records
which tier produced the final algorithm label for each of the 100 benchmark
workloads. Outputs:

    latex/tier_attribution.json         raw per-workload records
    latex/tier_attribution_summary.tex  LaTeX \\newcommand macros for the paper

Tier attribution follows the same decision tree used in production:

  - Tier 1 "CodeBERT confident":
      CodeBERT returned >=1 algo at prob >= 0.5
      AND rule-based did NOT override (rule_conf < 0.7
      OR rule_algos[0] in codebert_algos)
      AND final algorithm_confidence >= 0.5

  - Tier 3 "rule-based cross-validated":
      CodeBERT returned something
      AND rule_confidence >= 0.7
      AND rule_algos[0] not in codebert_algos

  - Tier 3 "rule-based low-conf fallback":
      CodeBERT/ML below 0.5 final confidence

  - Tier 2 "ML ensemble":
      CodeBERT unavailable or returned nothing (very rare: CodeBERT
      always populates top-1 as a fallback inside the classifier itself)

Only the 46 quantum + 24 hybrid workloads execute the tier pipeline; the 32
classical workloads skip algorithm detection entirely (see main.py line 211
`if is_quantum:`). Those are tagged "non-quantum (skipped)".
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
ENGINE_DIR = SCRIPT_DIR.parent
REPO_ROOT = ENGINE_DIR.parent
sys.path.insert(0, str(ENGINE_DIR))

from modules.ast_builder import ASTBuilder  # noqa: E402
from modules.algorithm_detector import QuantumAlgorithmDetector  # noqa: E402
from modules.codebert_algorithm_classifier import CodeBERTAlgorithmClassifier  # noqa: E402
from modules.language_detector import SupportedLanguage  # noqa: E402
from modules.ml_language_classifier import MLLanguageClassifier  # noqa: E402

WORKLOADS_DIR = REPO_ROOT / "benchmarks" / "workloads"
OUT_JSON = REPO_ROOT / "latex" / "tier_attribution.json"
OUT_TEX = REPO_ROOT / "latex" / "tier_attribution_summary.tex"

QUANTUM_LANGS = {
    SupportedLanguage.QISKIT,
    SupportedLanguage.CIRQ,
    SupportedLanguage.OPENQASM,
    SupportedLanguage.QSHARP,
}


def classify_tier(
    code: str,
    ast_builder: ASTBuilder,
    ml_lang: MLLanguageClassifier,
    codebert: CodeBERTAlgorithmClassifier,
    rule_detector: QuantumAlgorithmDetector,
) -> Dict:
    """Run the production tier-selection pipeline on one workload.

    Returns a dict with the winning tier label and diagnostic fields.
    """
    lang_result = ml_lang.detect(code=code)
    detected_lang_str = lang_result.get("language")
    try:
        detected_lang = SupportedLanguage(detected_lang_str)
    except Exception:
        detected_lang = None

    is_quantum = detected_lang in QUANTUM_LANGS

    if not is_quantum:
        return {
            "tier": "non-quantum (skipped)",
            "language": detected_lang_str,
            "is_quantum": False,
            "codebert_algos": [],
            "codebert_conf": 0.0,
            "rule_algos": [],
            "rule_conf": 0.0,
            "final_algos": [],
            "final_source": None,
        }

    # Tier 1: CodeBERT
    codebert_result = codebert.classify(code=code, threshold=0.5)
    codebert_algos = codebert_result.get("algorithms", [])
    codebert_conf = float(codebert_result.get("confidence", 0.0))

    # Rule-based detector (always runs for cross-validation)
    unified_ast = ast_builder.build(code, detected_lang)
    rule_result = rule_detector.detect(unified_ast)
    rule_algos = rule_result.get("detected_algorithms", [])
    rule_conf = float(rule_result.get("confidence", 0.0))

    detected_algos = list(codebert_algos)
    algo_conf = codebert_conf
    source = "codebert"

    # Cross-validation: rule-based override on disagreement with high conf
    if detected_algos and rule_conf >= 0.7 and rule_algos and rule_algos[0] not in detected_algos:
        detected_algos = rule_algos
        algo_conf = rule_conf
        source = "rule-based (cross-validated)"

    # Low-confidence fallback to rule-based
    if not detected_algos or algo_conf < 0.5:
        if rule_algos:
            detected_algos = rule_algos
            algo_conf = rule_conf
            source = "rule-based (low-conf fallback)"

    # Tier attribution from final source
    if source == "codebert":
        tier = "tier-1 (CodeBERT)"
    elif source == "rule-based (cross-validated)":
        tier = "tier-3 (rule cross-validated)"
    elif source == "rule-based (low-conf fallback)":
        tier = "tier-3 (rule fallback)"
    else:
        tier = "tier-2 (ML ensemble)"

    return {
        "tier": tier,
        "language": detected_lang_str,
        "is_quantum": True,
        "codebert_algos": codebert_algos,
        "codebert_conf": round(codebert_conf, 4),
        "rule_algos": rule_algos,
        "rule_conf": round(rule_conf, 4),
        "final_algos": detected_algos,
        "final_source": source,
    }


def main() -> None:
    ml_lang = MLLanguageClassifier()
    ast_builder = ASTBuilder()
    codebert = CodeBERTAlgorithmClassifier()
    codebert.load_models()
    rule_detector = QuantumAlgorithmDetector()

    records: List[Dict] = []
    workload_files = sorted(
        list(WORKLOADS_DIR.rglob("*.py")) + list(WORKLOADS_DIR.rglob("*.qasm"))
    )
    for workload_file in workload_files:
        if "__pycache__" in str(workload_file):
            continue
        try:
            code = workload_file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"skip {workload_file.name}: {e}")
            continue

        rec = classify_tier(code, ast_builder, ml_lang, codebert, rule_detector)
        rec["workload_name"] = workload_file.stem
        rec["folder"] = workload_file.parent.name
        records.append(rec)
        print(f"  {workload_file.parent.name}/{workload_file.stem}: {rec['tier']}")

    # Summary counts
    tier_counts: Dict[str, int] = {}
    for r in records:
        tier_counts[r["tier"]] = tier_counts.get(r["tier"], 0) + 1

    total = len(records)
    n_quantum = sum(1 for r in records if r["is_quantum"])
    n_classical_skipped = total - n_quantum

    print("\n=== Tier attribution summary ===")
    print(f"Total workloads: {total}")
    print(f"Non-quantum (skipped tier pipeline): {n_classical_skipped}")
    print(f"Quantum (ran tier pipeline): {n_quantum}")
    for t, c in sorted(tier_counts.items()):
        share = 100.0 * c / total
        quantum_share = 100.0 * c / n_quantum if n_quantum > 0 else 0.0
        print(f"  {t}: {c} ({share:.1f}% of all, {quantum_share:.1f}% of quantum)")

    # Save raw JSON
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({
            "total_workloads": total,
            "non_quantum_skipped": n_classical_skipped,
            "quantum_evaluated": n_quantum,
            "tier_counts": tier_counts,
            "records": records,
        }, f, indent=2)

    # Helper: extract counts by specific tier name
    def count(key: str) -> int:
        return tier_counts.get(key, 0)

    tier1 = count("tier-1 (CodeBERT)")
    tier2 = count("tier-2 (ML ensemble)")
    tier3_cross = count("tier-3 (rule cross-validated)")
    tier3_fb = count("tier-3 (rule fallback)")
    tier3_total = tier3_cross + tier3_fb

    def pct(n: int, d: int) -> str:
        return f"{100.0 * n / d:.1f}" if d > 0 else "0.0"

    # LaTeX macros file
    tex = [
        "% Auto-generated by tier_attribution_analysis.py.",
        "% DO NOT EDIT BY HAND.",
        "% These macros back the tier-attribution claims in Section~IV.C.",
        f"\\newcommand{{\\tierTotalWorkloads}}{{{total}}}",
        f"\\newcommand{{\\tierQuantumEvaluated}}{{{n_quantum}}}",
        f"\\newcommand{{\\tierNonQuantumSkipped}}{{{n_classical_skipped}}}",
        f"\\newcommand{{\\tierOneCount}}{{{tier1}}}",
        f"\\newcommand{{\\tierOneShareQuantum}}{{{pct(tier1, n_quantum)}}}",
        f"\\newcommand{{\\tierTwoCount}}{{{tier2}}}",
        f"\\newcommand{{\\tierTwoShareQuantum}}{{{pct(tier2, n_quantum)}}}",
        f"\\newcommand{{\\tierThreeCount}}{{{tier3_total}}}",
        f"\\newcommand{{\\tierThreeShareQuantum}}{{{pct(tier3_total, n_quantum)}}}",
        f"\\newcommand{{\\tierThreeCrossCount}}{{{tier3_cross}}}",
        f"\\newcommand{{\\tierThreeFallbackCount}}{{{tier3_fb}}}",
        "",
    ]
    with open(OUT_TEX, "w", encoding="utf-8") as f:
        f.write("\n".join(tex))

    print(f"\nWrote {OUT_JSON}")
    print(f"Wrote {OUT_TEX}")


if __name__ == "__main__":
    main()
