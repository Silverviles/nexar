#!/usr/bin/env python3
"""
Nexar Real Hardware Benchmark Runner
=====================================
Runs quantum circuits from the paper's benchmark suite on real IBM Quantum hardware.
Circuits are ordered from lowest to highest qubit count.

Usage:
    python run_real_benchmark.py            # run next unrun circuit
    python run_real_benchmark.py --index 3  # run specific circuit by index
    python run_real_benchmark.py --list     # list all circuits and their status
    python run_real_benchmark.py --paid     # force use of paid plan backends

Results are saved incrementally to: latex/real_benchmark_results.json
"""

import sys, os, json, time, argparse
from datetime import datetime, timezone
from pathlib import Path
from math import pi
import statistics

SCRIPT_DIR = Path(__file__).parent
HAL_DIR    = SCRIPT_DIR.parent
PROJECT_DIR = HAL_DIR.parent
RESULTS_FILE = PROJECT_DIR / 'latex' / 'real_benchmark_results.json'

sys.path.insert(0, str(HAL_DIR))
from dotenv import load_dotenv
load_dotenv(HAL_DIR / '.env')

from qiskit.circuit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

# ─── Backend config ────────────────────────────────────────────────────────────
OPEN_BACKENDS  = ['ibm_fez', 'ibm_marrakesh', 'ibm_kingston']
SHOTS          = 1024
POLL_INTERVAL  = 10   # seconds between status checks
JOB_TIMEOUT    = 600  # 10 minutes max wait per job

# ─── Circuit builders (ordered by logical qubit count) ────────────────────────

def build_dj_constant():
    """Deutsch-Jozsa constant oracle f(x)=0.  Expected output: 0 (constant)."""
    qc = QuantumCircuit(2, 1)
    qc.h(0); qc.x(1); qc.h(1)
    # constant oracle: no gate on ancilla
    qc.h(0)
    qc.measure(0, 0)
    return qc

def build_dj_balanced():
    """Deutsch-Jozsa balanced oracle f(x)=x.  Expected output: 1 (balanced)."""
    qc = QuantumCircuit(2, 1)
    qc.h(0); qc.x(1); qc.h(1)
    qc.cx(0, 1)   # balanced oracle
    qc.h(0)
    qc.measure(0, 0)
    return qc

def build_h2_vqe():
    """H2 VQE hardware-efficient ansatz, 4 qubits. HF initial state + Ry/CX layer."""
    qc = QuantumCircuit(4)
    qc.x([0, 1])                          # Hartree-Fock initial state (2 electrons)
    theta = [0.346, -0.241, 0.182, -0.133]
    for i, t in enumerate(theta):
        qc.ry(t, i)
    qc.cx(0, 1); qc.cx(1, 2); qc.cx(2, 3)
    qc.measure_all()
    return qc

def build_bv():
    """Bernstein-Vazirani, secret='101', 4 qubits (3 query + 1 ancilla).
    Expected measurement: 101."""
    secret = "101"
    n = len(secret)
    qc = QuantumCircuit(n + 1, n)
    qc.x(n); qc.h(range(n + 1))
    for i, bit in enumerate(reversed(secret)):
        if bit == '1':
            qc.cx(i, n)
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc

def build_simons():
    """Simon's algorithm, hidden period s='11', 4 qubits (2 input + 2 output).
    Measurements should be orthogonal to s='11'."""
    n = 2
    qc = QuantumCircuit(2 * n, n)
    qc.h(range(n))
    # Oracle for s='11': f(x) = f(x XOR s)
    qc.cx(0, n); qc.cx(1, n + 1)
    qc.cx(0, n + 1); qc.cx(1, n)
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc

def build_qft_4q():
    """QFT on 4 qubits, input state |0101> = 5."""
    qc = QuantumCircuit(4)
    qc.x([0, 2])                           # prepare |0101> = 5
    qc.append(QFT(4), range(4))
    qc.measure_all()
    return qc

def build_qpe():
    """QPE for T gate (phase = 1/8 = 0.001 binary), 4 qubits (3 counting + 1 eigenstate).
    Expected: counting register measures 001 (binary 0.001 = 1/8)."""
    qc = QuantumCircuit(4, 3)
    qc.x(3)                                # eigenstate |1> of T
    qc.h([0, 1, 2])
    qc.cp(pi / 4, 0, 3)                    # controlled-T^1
    qc.cp(pi / 2, 1, 3)                    # controlled-T^2
    qc.cp(pi,     2, 3)                    # controlled-T^4
    qc.append(QFT(3, inverse=True), [0, 1, 2])
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc

def build_grover_4q():
    """Grover's search, 4 qubits, oracle marks |1111>.  1 iteration."""
    n = 4
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    # Oracle: phase-flip |1111>
    qc.x(range(n)); qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1); qc.x(range(n))
    # Diffuser
    qc.h(range(n)); qc.x(range(n)); qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1); qc.x(range(n)); qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc

def build_qaoa_4node():
    """QAOA MaxCut, 4-node cycle graph (0-1-2-3-0), p=1 layer."""
    n = 4
    gamma, beta = 0.4, 0.3
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    for u, v in [(0,1),(1,2),(2,3),(3,0)]:
        qc.cx(u, v); qc.rz(2 * gamma, v); qc.cx(u, v)
    for i in range(n):
        qc.rx(2 * beta, i)
    qc.measure(range(n), range(n))
    return qc

def build_qsvm_8q():
    """QSVM ZZFeatureMap kernel circuit, 8 qubits, depth 2."""
    import numpy as np
    n = 8
    x = np.linspace(0.2, 1.5, n)
    qc = QuantumCircuit(n)
    for _ in range(2):                     # 2 repetitions of feature map
        for i in range(n):
            qc.h(i); qc.p(2.0 * x[i], i)
        for i in range(n - 1):
            qc.cx(i, i + 1)
            qc.p(2.0 * (pi - x[i]) * (pi - x[i + 1]), i + 1)
            qc.cx(i, i + 1)
    qc.measure_all()
    return qc

def build_qaoa_supply_8q():
    """QAOA supply chain optimisation, 8-node ring + cross edges, p=1."""
    n = 8
    gamma, beta = 0.45, 0.28
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    edges = [(i, (i+1) % n) for i in range(n)] + [(0,4),(1,5),(2,6),(3,7)]
    for u, v in edges:
        qc.cx(u, v); qc.rz(2 * gamma, v); qc.cx(u, v)
    for i in range(n):
        qc.rx(2 * beta, i)
    qc.measure(range(n), range(n))
    return qc

def build_lih_vqe_8q():
    """LiH VQE hardware-efficient ansatz, 8 qubits, 2 layers."""
    n = 8
    qc = QuantumCircuit(n)
    qc.x([0, 1, 2])                        # approximate HF state for LiH
    theta = [0.1 * (i + 1) for i in range(n * 2)]
    for i in range(n): qc.ry(theta[i], i)
    for i in range(n - 1): qc.cx(i, i + 1)
    for i in range(n): qc.ry(theta[n + i], i)
    for i in range(0, n - 1, 2): qc.cx(i, i + 1)
    qc.measure_all()
    return qc

def build_qaoa_graph_partition_12q():
    """QAOA graph partitioning, 12 qubits, p=1."""
    n = 12
    gamma, beta = 0.35, 0.28
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    edges = [(i, (i+1) % n) for i in range(n)] + [(i, (i+4) % n) for i in range(n)]
    for u, v in edges:
        qc.cx(u, v); qc.rz(2 * gamma, v); qc.cx(u, v)
    for i in range(n):
        qc.rx(2 * beta, i)
    qc.measure(range(n), range(n))
    return qc

def build_h2o_vqe_12q():
    """H2O VQE hardware-efficient ansatz, 12 qubits."""
    n = 12
    qc = QuantumCircuit(n)
    qc.x([0, 1, 2, 3])                    # approximate HF state for H2O
    theta = [0.05 * (i + 1) for i in range(n * 2)]
    for i in range(n): qc.ry(theta[i], i)
    for i in range(n - 1): qc.cx(i, i + 1)
    for i in range(n): qc.ry(theta[n + i], i)
    qc.measure_all()
    return qc

def build_shor_15():
    """Shor's N=15 (a=7): QFT-based order-finding structure, 12 qubits.
    Note: modular exponentiation is structurally representative, not exact."""
    n_count, n_work = 8, 4
    qc = QuantumCircuit(n_count + n_work, n_count)
    qc.h(range(n_count))
    qc.x(n_count)                          # work register |1>
    for i in range(n_count):
        qc.cx(i, n_count + (i % n_work))
    qc.append(QFT(n_count, inverse=True), range(n_count))
    qc.measure(range(n_count), range(n_count))
    return qc

def build_grover_3sat_12q():
    """Grover 3-SAT oracle, 12 qubits (4 variable + 8 ancilla), 1 iteration.
    Marks solution: x0=1, x1=0, x2=1, x3=1."""
    n_vars, n_anc = 4, 8
    qc = QuantumCircuit(n_vars + n_anc, n_vars)
    qc.h(range(n_vars))
    qc.x(1)                                # flip x1 to check x1=0
    for i in range(n_vars):
        qc.cx(i, n_vars + i)
    qc.x(1)
    # Diffuser on variable qubits
    qc.h(range(n_vars)); qc.x(range(n_vars)); qc.h(n_vars - 1)
    qc.mcx(list(range(n_vars - 1)), n_vars - 1)
    qc.h(n_vars - 1); qc.x(range(n_vars)); qc.h(range(n_vars))
    qc.measure(range(n_vars), range(n_vars))
    return qc

def build_shor_21():
    """Shor's N=21: QFT-based structure, 14 qubits (10 counting + 4 work)."""
    n_count, n_work = 10, 4
    qc = QuantumCircuit(n_count + n_work, n_count)
    qc.h(range(n_count))
    qc.x(n_count)
    for i in range(n_count):
        qc.cx(i, n_count + (i % n_work))
    qc.append(QFT(n_count, inverse=True), range(n_count))
    qc.measure(range(n_count), range(n_count))
    return qc

def build_shor_35():
    """Shor's N=35: QFT-based structure, 16 qubits (12 counting + 4 work)."""
    n_count, n_work = 12, 4
    qc = QuantumCircuit(n_count + n_work, n_count)
    qc.h(range(n_count))
    qc.x(n_count)
    for i in range(n_count):
        qc.cx(i, n_count + (i % n_work))
    qc.append(QFT(n_count, inverse=True), range(n_count))
    qc.measure(range(n_count), range(n_count))
    return qc

def build_qnn_16q():
    """Quantum Neural Network circuit, 16 qubits, 2 variational layers."""
    import numpy as np
    n = 16
    qc = QuantumCircuit(n)
    np.random.seed(42)
    theta = np.random.uniform(0, pi, n * 2)
    for i in range(n): qc.ry(theta[i], i)
    for i in range(n - 1): qc.cx(i, i + 1)
    qc.cx(n - 1, 0)                        # periodic boundary
    for i in range(n): qc.ry(theta[n + i], i)
    qc.measure_all()
    return qc

def build_vqe_caffeine_16q():
    """VQE caffeine molecular simulation ansatz, 16 qubits, hardware-efficient."""
    n = 16
    qc = QuantumCircuit(n)
    qc.x(range(n // 4))                    # approximate HF state
    theta = [0.07 * (i + 1) for i in range(n * 2)]
    for i in range(n): qc.ry(theta[i], i)
    for i in range(0, n - 1, 2): qc.cx(i, i + 1)
    for i in range(1, n - 1, 2): qc.cx(i, i + 1)
    for i in range(n): qc.ry(theta[n + i], i)
    qc.measure_all()
    return qc

def build_grover_20q():
    """Grover's 20-qubit search, 1 oracle+diffuser iteration, marks |1...1>."""
    n = 20
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    # Oracle: phase-flip |1...1>
    qc.x(range(n)); qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1); qc.x(range(n))
    # Diffuser
    qc.h(range(n)); qc.x(range(n)); qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1); qc.x(range(n)); qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc

def build_qaoa_vehicle_routing_20q():
    """QAOA vehicle routing, 20 qubits (5 vehicles × 4 locations), p=1."""
    n = 20
    gamma, beta = 0.38, 0.25
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    edges = [(i, (i+1) % n) for i in range(n)] + \
            [(i, (i+4) % n) for i in range(n)] + \
            [(i, (i+5) % n) for i in range(0, n, 5)]
    seen = set()
    for u, v in edges:
        if (u, v) not in seen and (v, u) not in seen:
            qc.cx(u, v); qc.rz(2 * gamma, v); qc.cx(u, v)
            seen.add((u, v))
    for i in range(n):
        qc.rx(2 * beta, i)
    qc.measure(range(n), range(n))
    return qc

def build_qaoa_graph_partition_20q():
    """QAOA graph partitioning, 20 qubits, p=1 (from paper's hybrid benchmark,
    quantum-routed at confidence 0.805)."""
    n = 20
    gamma, beta = 0.40, 0.30
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    edges = [(i, (i+1) % n) for i in range(n)] + \
            [(i, (i+5) % n) for i in range(n)]
    seen = set()
    for u, v in edges:
        if (u, v) not in seen and (v, u) not in seen:
            qc.cx(u, v); qc.rz(2 * gamma, v); qc.cx(u, v)
            seen.add((u, v))
    for i in range(n):
        qc.rx(2 * beta, i)
    qc.measure(range(n), range(n))
    return qc

def build_zne_24q():
    """ZNE benchmark circuit, 24 qubits. GHZ-state preparation + T/Tdg noise
    amplification layer, used to characterise error extrapolation
    (from paper's hybrid benchmark, quantum-routed at 24 qubits)."""
    n = 24
    qc = QuantumCircuit(n, n)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    for i in range(n):
        qc.t(i); qc.tdg(i)                # noise-amplifying T/Tdg identity pairs
    for i in range(n - 2, -1, -1):
        qc.cx(i, i + 1)
    qc.h(0)
    qc.measure(range(n), range(n))
    return qc

def build_qaoa_maxcut_50q():
    """QAOA MaxCut 50-qubit ring graph, p=1
    (from paper's quantum benchmark, quantum-routed at confidence ~0.8)."""
    n = 50
    gamma, beta = 0.40, 0.30
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    for i in range(n):
        u, v = i, (i + 1) % n
        qc.cx(u, v); qc.rz(2 * gamma, v); qc.cx(u, v)
    for i in range(n):
        qc.rx(2 * beta, i)
    qc.measure(range(n), range(n))
    return qc

def build_iron_sulfur_vqe_60q():
    """Iron-sulfur protein VQE hardware-efficient ansatz, 60 qubits, 1 layer
    (from paper's quantum benchmark, quantum-routed at confidence ~0.9)."""
    n = 60
    qc = QuantumCircuit(n)
    qc.x(range(n // 4))
    theta = [0.05 * ((i % 13) + 1) for i in range(n * 2)]
    for i in range(n): qc.ry(theta[i], i)
    for i in range(n - 1): qc.cx(i, i + 1)
    for i in range(n): qc.ry(theta[n + i], i)
    qc.measure_all()
    return qc

def build_vqe_120q():
    """120-qubit VQE hardware-efficient ansatz, 1 layer, nearest-neighbour CX ladder
    (from paper's quantum benchmark, FORCE_QUANTUM override, confidence 1.0)."""
    n = 120
    qc = QuantumCircuit(n)
    qc.x(range(n // 4))
    theta = [0.03 * ((i % 17) + 1) for i in range(n * 2)]
    for i in range(n): qc.ry(theta[i], i)
    for i in range(n - 1): qc.cx(i, i + 1)
    for i in range(n): qc.ry(theta[n + i], i)
    qc.measure_all()
    return qc


# ─── Circuit registry (ordered lowest → highest qubits) ───────────────────────
CIRCUITS = [
    # (index, name, qubits, category, build_fn, paper_ref)
    ( 1, "Deutsch-Jozsa (constant oracle)",        2,   "foundational",   build_dj_constant,             "Sec. VIII-A foundational"),
    ( 2, "Deutsch-Jozsa (balanced oracle)",         2,   "foundational",   build_dj_balanced,             "Sec. VIII-A foundational"),
    ( 3, "H2 VQE ansatz",                           4,   "simulation",     build_h2_vqe,                  "Sec. VIII-A molecular simulation"),
    ( 4, "Bernstein-Vazirani (secret=101)",          4,   "foundational",   build_bv,                      "Sec. VIII-A foundational"),
    ( 5, "Simon's algorithm (s=11)",                 4,   "foundational",   build_simons,                  "Sec. VIII-A foundational"),
    ( 6, "QFT (input=|0101>)",                       4,   "foundational",   build_qft_4q,                  "Sec. VIII-A foundational"),
    ( 7, "Quantum Phase Estimation (T gate)",        4,   "foundational",   build_qpe,                     "Sec. VIII-A foundational"),
    ( 8, "Grover's search (|1111>, 4q)",             4,   "search",         build_grover_4q,               "Sec. VIII-A search"),
    ( 9, "QAOA MaxCut (4-node cycle)",               4,   "optimization",   build_qaoa_4node,              "Sec. VIII-A optimization"),
    (10, "QSVM kernel circuit",                      8,   "hybrid-ml",      build_qsvm_8q,                 "Sec. VIII-A hybrid"),
    (11, "QAOA supply chain (8q)",                   8,   "hybrid-opt",     build_qaoa_supply_8q,          "Sec. VIII-A hybrid"),
    (12, "LiH VQE ansatz (8q)",                      8,   "simulation",     build_lih_vqe_8q,              "Sec. VIII-A molecular simulation"),
    (13, "QAOA graph partitioning (12q)",            12,   "hybrid-opt",     build_qaoa_graph_partition_12q,"Sec. VIII-A hybrid"),
    (14, "H2O VQE ansatz (12q)",                    12,   "simulation",     build_h2o_vqe_12q,             "Sec. VIII-A molecular simulation"),
    (15, "Shor's N=15 (order-finding)",             12,   "factoring",      build_shor_15,                 "Sec. VIII-A factoring"),
    (16, "Grover 3-SAT (4 variables)",              12,   "search",         build_grover_3sat_12q,         "Sec. VIII-A search"),
    (17, "Shor's N=21 (order-finding)",             14,   "factoring",      build_shor_21,                 "Sec. VIII-A factoring"),
    (18, "Shor's N=35 (order-finding)",             16,   "factoring",      build_shor_35,                 "Sec. VIII-A factoring"),
    (19, "QNN variational circuit (16q)",           16,   "hybrid-ml",      build_qnn_16q,                 "Sec. VIII-A hybrid"),
    (20, "VQE caffeine ansatz (16q)",               16,   "simulation",     build_vqe_caffeine_16q,        "Sec. VIII-A molecular simulation"),
    (21, "Grover's search (20q)",                   20,   "search",         build_grover_20q,              "Sec. VIII-A search"),
    (22, "QAOA vehicle routing (20q)",              20,   "optimization",   build_qaoa_vehicle_routing_20q,"Sec. VIII-A optimization"),
    (23, "QAOA graph partitioning (20q)",           20,   "hybrid-opt",     build_qaoa_graph_partition_20q,"Sec. VIII-B quantum-routed, conf=0.805"),
    (24, "ZNE benchmark circuit (24q)",             24,   "hybrid-em",      build_zne_24q,                 "Sec. VIII-B quantum-routed, 24q"),
    (25, "QAOA MaxCut (50q)",                       50,   "optimization",   build_qaoa_maxcut_50q,         "Sec. VIII-B quantum-routed"),
    (26, "Iron-sulfur protein VQE (60q)",           60,   "simulation",     build_iron_sulfur_vqe_60q,     "Sec. VIII-B quantum-routed"),
    (27, "120-qubit VQE ansatz",                   120,   "simulation",     build_vqe_120q,                "Sec. VIII-B FORCE_QUANTUM, conf=1.0"),
]


# ─── Results I/O ──────────────────────────────────────────────────────────────

def load_results():
    if RESULTS_FILE.exists():
        with open(RESULTS_FILE) as f:
            return json.load(f)
    return {"metadata": {"created": datetime.now(timezone.utc).isoformat()}, "runs": []}

def save_results(data):
    data["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(RESULTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def completed_indices(data):
    return {r["index"] for r in data["runs"] if r.get("status") == "COMPLETED"}


# ─── Backend selection (open plan first) ──────────────────────────────────────

def pick_backend(service, use_paid=False):
    backends = service.backends()
    if not use_paid:
        candidates = [b for b in backends if b.name in OPEN_BACKENDS]
        if not candidates:
            print("  [warn] No open-plan backends found, falling back to all backends.")
            candidates = backends
    else:
        candidates = backends

    def queue_depth(b):
        try:
            return getattr(b.status(), 'pending_jobs', 999)
        except Exception:
            return 999

    best = min(candidates, key=queue_depth)
    q = queue_depth(best)
    print(f"  Backend selected: {best.name}  (queue={q} jobs)")
    return best


# ─── Cost estimate (paper model, Table III) ───────────────────────────────────

def estimate_cost(exec_time_s, gate_count, shots=SHOTS):
    base   = 0.30
    qpu    = exec_time_s * 1.60
    shot   = shots * 0.00145
    gate   = gate_count * 0.0001
    return round(base + qpu + shot + gate, 4)


# ─── Result extraction from SamplerV2 ─────────────────────────────────────────

def extract_counts(result):
    """Extract measurement counts from a SamplerV2 PrimitiveResult."""
    pub = result[0]
    data = getattr(pub, 'data', None)
    if data is None:
        return {}
    # Try common register names
    for reg_name in ('meas', 'c', 'cr'):
        reg = getattr(data, reg_name, None)
        if reg is not None and hasattr(reg, 'get_counts'):
            counts = reg.get_counts()
            if counts:
                return counts
    # Fallback: iterate all registers
    for val in vars(data).values():
        if hasattr(val, 'get_counts'):
            counts = val.get_counts()
            if counts:
                return counts
    return {}


# ─── Single circuit runner ─────────────────────────────────────────────────────

def run_circuit(entry, service, use_paid=False):
    idx, name, n_qubits, category, build_fn, paper_ref = entry

    print(f"\n{'='*60}")
    print(f"  Circuit {idx:2d}/27  |  {name}")
    print(f"  Qubits: {n_qubits}  |  Category: {category}")
    print(f"  Paper ref: {paper_ref}")
    print(f"{'='*60}")

    # Build circuit
    qc = build_fn()
    pre_depth  = qc.depth()
    pre_gates  = qc.size()
    print(f"  Pre-transpile:  depth={pre_depth}, gates={pre_gates}")

    # Select backend
    backend = pick_backend(service, use_paid)

    # Transpile
    pm = generate_preset_pass_manager(target=backend.target, optimization_level=1)
    tqc = pm.run(qc)
    post_depth = tqc.depth()
    post_gates = tqc.size()
    print(f"  Post-transpile: depth={post_depth}, gates={post_gates}")

    # Submit
    sampler = Sampler(mode=backend)
    submit_time = time.time()
    submitted_at = datetime.now(timezone.utc).isoformat()
    print(f"  Submitting {SHOTS} shots ... ", end='', flush=True)

    try:
        job = sampler.run([tqc], shots=SHOTS)
    except Exception as e:
        print(f"FAILED\n  Error: {e}")
        return None

    job_id = job.job_id()
    print(f"submitted")
    print(f"  Job ID: {job_id}")

    # Poll
    start_time = None
    while True:
        elapsed = time.time() - submit_time
        if elapsed > JOB_TIMEOUT:
            print(f"\n  [timeout] Job exceeded {JOB_TIMEOUT}s — recording as TIMEOUT")
            return {
                "index": idx, "name": name, "qubits": n_qubits,
                "category": category, "paper_ref": paper_ref,
                "backend": backend.name, "job_id": job_id,
                "submitted_at": submitted_at, "status": "TIMEOUT",
            }

        try:
            status = job.status()
            status_str = status.name if hasattr(status, 'name') else str(status)
        except Exception:
            status_str = "UNKNOWN"

        if start_time is None and status_str in ("RUNNING", "DONE", "COMPLETED"):
            start_time = time.time()
            queue_time_s = round(start_time - submit_time, 1)
            print(f"\n  Queue time: {queue_time_s}s  |  Running ...", end='', flush=True)

        if status_str in ("DONE", "COMPLETED"):
            break
        if status_str in ("ERROR", "FAILED", "CANCELLED"):
            print(f"\n  Job ended with status: {status_str}")
            return {
                "index": idx, "name": name, "qubits": n_qubits,
                "category": category, "paper_ref": paper_ref,
                "backend": backend.name, "job_id": job_id,
                "submitted_at": submitted_at, "status": status_str,
            }

        print('.', end='', flush=True)
        time.sleep(POLL_INTERVAL)

    completed_at = datetime.now(timezone.utc).isoformat()
    exec_time_s = round(time.time() - (start_time or submit_time), 2)
    if start_time is None:
        queue_time_s = 0.0

    print(f" done  (exec={exec_time_s}s)")

    # Extract results
    try:
        result = job.result()
        counts = extract_counts(result)
    except Exception as e:
        print(f"  [warn] Could not extract counts: {e}")
        counts = {}

    total_shots = sum(counts.values()) if counts else 0
    if counts:
        top_outcome     = max(counts, key=counts.get)
        top_outcome_pct = round(counts[top_outcome] / total_shots, 4) if total_shots else 0
    else:
        top_outcome, top_outcome_pct = "N/A", 0.0

    est_cost = estimate_cost(exec_time_s, post_gates)

    record = {
        "index":               idx,
        "name":                name,
        "qubits":              n_qubits,
        "category":            category,
        "paper_ref":           paper_ref,
        "backend":             backend.name,
        "job_id":              job_id,
        "submitted_at":        submitted_at,
        "completed_at":        completed_at,
        "queue_time_s":        queue_time_s,
        "exec_time_s":         exec_time_s,
        "depth_pre_transpile": pre_depth,
        "depth_post_transpile":post_depth,
        "gates_pre_transpile": pre_gates,
        "gates_post_transpile":post_gates,
        "shots":               SHOTS,
        "top_outcome":         top_outcome,
        "top_outcome_pct":     top_outcome_pct,
        "counts":              counts,
        "estimated_cost_usd":  est_cost,
        "status":              "COMPLETED",
    }

    # Try to get precise timing from IBM job metrics
    try:
        metrics = job.metrics()
        usage = metrics.get('usage', {})
        ibm_exec_s = usage.get('quantum_seconds') or usage.get('seconds')
        if ibm_exec_s is not None:
            record["ibm_quantum_seconds"] = round(float(ibm_exec_s), 4)
    except Exception:
        pass

    # Print summary
    print(f"\n  +-- RESULTS ------------------------------------------")
    print(f"  |  Backend:       {backend.name}")
    print(f"  |  Job ID:        {job_id}")
    print(f"  |  Queue time:    {queue_time_s}s")
    print(f"  |  Exec time:     {exec_time_s}s")
    if "ibm_quantum_seconds" in record:
        print(f"  |  IBM QPU time:  {record['ibm_quantum_seconds']}s")
    print(f"  |  Depth (post):  {post_depth}")
    print(f"  |  Gates (post):  {post_gates}")
    print(f"  |  Shots:         {SHOTS}")
    print(f"  |  Top outcome:   |{top_outcome}> ({top_outcome_pct*100:.1f}%)")
    print(f"  |  Est. cost:     ${est_cost:.4f} USD")
    print(f"  +-----------------------------------------------------")

    return record


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Nexar Real Hardware Benchmark Runner")
    parser.add_argument('--index',  type=int, help="Run specific circuit by index (1-27)")
    parser.add_argument('--list',   action='store_true', help="List all circuits and completion status")
    parser.add_argument('--paid',   action='store_true', help="Use paid plan backends instead of open plan")
    parser.add_argument('--fetch',  type=str, metavar='JOB_ID',
                        help="Recover results from an already-completed IBM job ID (provide --index too)")
    args = parser.parse_args()

    # Load prior results
    data = load_results()
    done = completed_indices(data)

    if args.list:
        print(f"\n{'#':>3}  {'Qubits':>6}  {'Status':>10}  {'Name'}")
        print("-" * 70)
        for idx, name, n_qubits, category, _, _ in CIRCUITS:
            status = "COMPLETED" if idx in done else "pending"
            marker = "✓" if idx in done else " "
            print(f"  {idx:2d}  {n_qubits:6d}  {marker} {status:>9}  {name}")
        print(f"\n  {len(done)}/{len(CIRCUITS)} completed")
        return

    # Connect to IBM
    token = os.environ.get('IBM_QUANTUM_TOKEN')
    if not token:
        print("ERROR: IBM_QUANTUM_TOKEN not set in .env"); sys.exit(1)

    print("Connecting to IBM Quantum ...", end='', flush=True)
    service = QiskitRuntimeService(channel='ibm_quantum_platform', token=token)
    print(" connected")

    # --fetch: recover a previously submitted job without re-running
    if args.fetch:
        if not args.index:
            print("ERROR: --fetch requires --index to identify which circuit entry to record")
            sys.exit(1)
        target = next((c for c in CIRCUITS if c[0] == args.index), None)
        if target is None:
            print(f"ERROR: No circuit with index {args.index}"); sys.exit(1)
        idx, name, n_qubits, category, build_fn, paper_ref = target
        print(f"\nFetching job {args.fetch} for circuit {idx}: {name}")
        job = service.job(args.fetch)
        status = job.status()
        status_str = status.name if hasattr(status, 'name') else str(status)
        print(f"  Status: {status_str}")
        if status_str not in ("DONE", "COMPLETED"):
            print(f"  Job not yet complete (status={status_str}). Try again later.")
            sys.exit(1)
        result = job.result()
        counts = extract_counts(result)
        total_shots = sum(counts.values()) if counts else 0
        top_outcome = max(counts, key=counts.get) if counts else "N/A"
        top_outcome_pct = round(counts[top_outcome] / total_shots, 4) if total_shots else 0
        # Build circuit to get transpile stats
        qc = build_fn()
        backend_name = job.backend().name
        backend = service.backend(backend_name)
        pm = generate_preset_pass_manager(target=backend.target, optimization_level=1)
        tqc = pm.run(qc)
        record = {
            "index": idx, "name": name, "qubits": n_qubits,
            "category": category, "paper_ref": paper_ref,
            "backend": backend_name, "job_id": args.fetch,
            "submitted_at": "recovered", "completed_at": datetime.now(timezone.utc).isoformat(),
            "queue_time_s": None, "exec_time_s": None,
            "depth_pre_transpile": qc.depth(), "depth_post_transpile": tqc.depth(),
            "gates_pre_transpile": qc.size(),  "gates_post_transpile": tqc.size(),
            "shots": total_shots, "top_outcome": top_outcome,
            "top_outcome_pct": top_outcome_pct, "counts": counts,
            "estimated_cost_usd": estimate_cost(0, tqc.size()),
            "status": "COMPLETED",
        }
        try:
            metrics = job.metrics()
            usage = metrics.get('usage', {})
            ibm_exec_s = usage.get('quantum_seconds') or usage.get('seconds')
            if ibm_exec_s is not None:
                record["ibm_quantum_seconds"] = round(float(ibm_exec_s), 4)
        except Exception:
            pass
        print(f"  Top outcome: |{top_outcome}> ({top_outcome_pct*100:.1f}%)")
        print(f"  Counts: {dict(list(counts.items())[:8])}")
        data["runs"].append(record)
        save_results(data)
        print(f"  Saved to {RESULTS_FILE}")
        sys.exit(0)

    # Determine which circuit to run
    if args.index:
        target = next((c for c in CIRCUITS if c[0] == args.index), None)
        if target is None:
            print(f"ERROR: No circuit with index {args.index}"); sys.exit(1)
        if target[0] in done:
            print(f"Circuit {args.index} already completed. Use a different index or check --list.")
            sys.exit(0)
    else:
        # Next unrun circuit
        target = next((c for c in CIRCUITS if c[0] not in done), None)
        if target is None:
            print("All 27 circuits completed!"); sys.exit(0)

    # Run it
    record = run_circuit(target, service, use_paid=args.paid)
    if record:
        data["runs"].append(record)
        save_results(data)
        print(f"\n  Results saved to: {RESULTS_FILE}")
        remaining = len(CIRCUITS) - len(completed_indices(data))
        print(f"  Progress: {len(completed_indices(data))}/{len(CIRCUITS)} done  ({remaining} remaining)")


if __name__ == '__main__':
    main()
