#!/usr/bin/env python3
"""
Nexar Pipeline Benchmark Runner
Calls Code Analysis Engine (8002) and Decision Engine (8003) directly.
"""
import argparse
import json
import csv
import os
import time
import urllib.request
import urllib.error
from pathlib import Path

# Mapping tables (from api/src/services/analysis-to-decision-mapper.ts)
PROBLEM_TYPE_MAP = {
    "search": "search",
    "optimization": "optimization",
    "simulation": "simulation",
    "factorization": "factorization",
    "machine_learning": "matrix_ops",
    "cryptography": "factorization",
    "sampling": "random_circuit",
    "oracle_identification": "search",
    "property_testing": "search",
    "hidden_structure": "factorization",
    "classical": "sorting",
    "unknown": "optimization",
}

TIME_COMPLEXITY_MAP = {
    "O(1)": "polynomial",
    "O(log n)": "polynomial",
    "O(n)": "polynomial",
    "O(n log n)": "nlogn",
    "O(n^2)": "polynomial",
    "O(n^3)": "polynomial",
    "O(n^k)": "polynomial",
    "O(2^n)": "exponential",
    "O(n!)": "exponential",
    "O(sqrt(n))": "quadratic_speedup",
    "unknown": "polynomial",
}


def load_workload(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def api_request(url, data=None, timeout=60):
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body)
    if body:
        req.add_header("Content-Type", "application/json")
    resp = urllib.request.urlopen(req, timeout=timeout)
    return json.loads(resp.read().decode("utf-8"))


def run_direct_pipeline(cae_url, de_url, code, timeout=300):
    """Call CAE then DE directly, mirroring the gateway pipeline."""
    result = {"status": "processing", "analysis": None, "decision": None,
              "mapped_input": None, "timing": {}, "error": None}

    # Step 1: Code Analysis
    t0 = time.time()
    try:
        analysis = api_request(
            f"{cae_url}/api/v1/code-analysis-engine/analyze",
            data={"code": code},
            timeout=timeout,
        )
        analysis_ms = int((time.time() - t0) * 1000)
        result["analysis"] = analysis
        result["timing"]["analysis_ms"] = analysis_ms
    except Exception as e:
        result["error"] = f"Analysis failed: {e}"
        result["status"] = "failed"
        return result

    # Step 2: Map analysis -> decision input
    mapped = {
        "problem_type": PROBLEM_TYPE_MAP.get(analysis.get("problem_type", ""), "optimization"),
        "problem_size": analysis.get("problem_size", 1),
        "qubits_required": analysis.get("qubits_required", 0),
        "circuit_depth": analysis.get("circuit_depth", 0),
        "gate_count": analysis.get("gate_count", 0),
        "cx_gate_ratio": analysis.get("cx_gate_ratio", 0),
        "superposition_score": analysis.get("superposition_score", 0),
        "entanglement_score": analysis.get("entanglement_score", 0),
        "time_complexity": TIME_COMPLEXITY_MAP.get(analysis.get("time_complexity", ""), "polynomial"),
        "memory_requirement_mb": analysis.get("memory_requirement_mb", 0),
    }
    result["mapped_input"] = mapped

    # Step 3: Decision Engine
    t1 = time.time()
    try:
        decision = api_request(
            f"{de_url}/api/v1/decision-engine/predict",
            data=mapped,
            timeout=60,
        )
        decision_ms = int((time.time() - t1) * 1000)
        result["decision"] = decision
        result["timing"]["decision_ms"] = decision_ms
    except Exception as e:
        result["error"] = f"Decision failed: {e}"
        result["status"] = "failed"
        return result

    result["timing"]["total_ms"] = analysis_ms + decision_ms
    result["status"] = "completed"
    return result


def flatten_result(workload_name, result):
    analysis = result.get("analysis") or {}
    decision = result.get("decision") or {}
    recommendation = decision.get("recommendation") or {}
    timing = result.get("timing") or {}

    detected_algs = analysis.get("detected_algorithms") or []
    if isinstance(detected_algs, list):
        detected_algs = ";".join(detected_algs)

    return {
        "workload_name": workload_name,
        "description": f"File: {workload_name}",
        "status": "completed" if not result.get("error") else "failed",
        "detected_language": analysis.get("detected_language", ""),
        "problem_type": analysis.get("problem_type", ""),
        "problem_size": analysis.get("problem_size", 0),
        "qubits_required": analysis.get("qubits_required", 0),
        "circuit_depth": analysis.get("circuit_depth", 0),
        "gate_count": analysis.get("gate_count", 0),
        "cx_gate_ratio": analysis.get("cx_gate_ratio", 0),
        "superposition_score": analysis.get("superposition_score", 0),
        "entanglement_score": analysis.get("entanglement_score", 0),
        "time_complexity": analysis.get("time_complexity", ""),
        "memory_mb": analysis.get("memory_requirement_mb", 0),
        "is_quantum": analysis.get("is_quantum", False),
        "detected_algorithms": detected_algs,
        "confidence_score": analysis.get("confidence_score", 0),
        "mapped_problem_type": (result.get("mapped_input") or {}).get("problem_type", ""),
        "mapped_time_complexity": (result.get("mapped_input") or {}).get("time_complexity", ""),
        "recommended_hardware": recommendation.get("recommended_hardware", ""),
        "decision_confidence": recommendation.get("confidence", 0),
        "quantum_probability": recommendation.get("quantum_probability", 0),
        "classical_probability": recommendation.get("classical_probability", 0),
        "rationale": recommendation.get("rationale", ""),
        "est_execution_time_ms": decision.get("estimated_execution_time_ms", 0),
        "est_cost_usd": decision.get("estimated_cost_usd", 0),
        "analysis_ms": timing.get("analysis_ms", 0),
        "decision_ms": timing.get("decision_ms", 0),
        "total_ms": timing.get("total_ms", 0),
        "error": result.get("error") or "",
    }


def discover_workloads(workloads_dir, recursive=True):
    workloads = []
    base = Path(workloads_dir)
    for ext in ("*.py", "*.qasm"):
        glob_pattern = f"**/{ext}" if recursive else ext
        for f in base.glob(glob_pattern):
            if f.name.startswith("__") or f.name.startswith("."):
                continue
            rel = f.relative_to(base)
            parts = list(rel.parts)
            name = f"{parts[0]}_{f.stem}" if len(parts) > 1 else f.stem
            workloads.append((name, str(f)))
    workloads.sort(key=lambda x: x[0])
    return workloads


def main():
    parser = argparse.ArgumentParser(description="Nexar Benchmark Pipeline")
    parser.add_argument("--token", default="", help="JWT auth token (unused in direct mode)")
    parser.add_argument("--dir", required=True, help="Workloads directory")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--api-url", default="http://localhost:3000", help="(unused in direct mode)")
    parser.add_argument("--cae-url", default="http://localhost:8002", help="Code Analysis Engine URL")
    parser.add_argument("--de-url", default="http://localhost:8003", help="Decision Engine URL")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    workloads = discover_workloads(args.dir, args.recursive)
    print(f"Found {len(workloads)} workloads\n")

    all_results = []
    csv_rows = []
    completed = 0
    failed = 0

    for i, (name, filepath) in enumerate(workloads, 1):
        print(f"[{i}/{len(workloads)}] {name} ... ", end="", flush=True)
        code = load_workload(filepath)

        try:
            result = run_direct_pipeline(args.cae_url, args.de_url, code, args.timeout)
            st = result.get("status", "unknown")
            if st == "completed":
                rec = (result.get("decision") or {}).get("recommendation") or {}
                hw = rec.get("recommended_hardware", "?")
                t = result["timing"].get("total_ms", 0)
                print(f"completed -> {hw} ({t}ms)")
                completed += 1
            else:
                print(f"FAILED: {result.get('error', 'unknown')}")
                failed += 1
        except Exception as e:
            result = {"error": str(e), "status": "failed"}
            print(f"ERROR: {e}")
            failed += 1

        all_results.append({"workload": name, "result": result})
        csv_rows.append(flatten_result(name, result))

    # Write JSON
    json_path = os.path.join(args.output_dir, "pipeline_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nJSON results: {json_path}")

    # Write CSV
    csv_path = os.path.join(args.output_dir, "pipeline_dataset.csv")
    if csv_rows:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
            writer.writeheader()
            writer.writerows(csv_rows)
    print(f"CSV results:  {csv_path}")
    print(f"\nDone: {completed} completed, {failed} failed, {len(all_results)} total")


if __name__ == "__main__":
    main()
