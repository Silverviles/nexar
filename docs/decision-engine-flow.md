# Decision Engine Evaluation Flow

```
                        ┌─────────────────────┐
                        │    User Input        │
                        │  (CodeAnalysisInput) │
                        └─────────┬───────────┘
                                  │
                 ┌────────────────┼────────────────┐
                 │                │                 │
                 ▼                ▼                 ▼
     ┌───────────────┐  ┌────────────────┐  ┌──────────────┐
     │   ML Model    │  │  Rule-Based    │  │    Cost      │
     │  (50% weight) │  │   System       │  │  Analyzer    │
     │               │  │  (35% weight)  │  │ (15% weight) │
     └───────┬───────┘  └───────┬────────┘  └──────┬───────┘
             │                  │                   │
             ▼                  ▼                   ▼
    ┌────────────────┐  ┌───────────────┐  ┌───────────────┐
    │ hardware:      │  │ decision_type │  │ quantum_cost  │
    │   Q or C       │  │ confidence    │  │ classical_cost│
    │ confidence     │  │ rationale     │  │ quantum_time  │
    │ quantum_prob   │  │ rules_fired   │  │ classical_time│
    │ classical_prob │  │               │  │ cost_optimal  │
    └────────┬───────┘  └───────┬───────┘  └───────┬───────┘
             │                  │                   │
             └──────────────────┼───────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Decision Merger     │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ HardwareRecommendation│
                    │ + Alternatives        │
                    │ + Cost/Time Estimates  │
                    └───────────────────────┘
```

## Rule-Based System (6-Step Evaluation)

The rule system can **force** a decision (bypassing ML and cost) or **defer** to the weighted merger.

```
Input
  │
  ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 1: Hardware Compatibility                                   │
│                                                                  │
│  Quantum checks:          Classical checks:                      │
│  • qubits ≤ 127           • memory ≤ 512 GB                     │
│  • circuit_depth ≤ 10000  • problem_size ≤ 1,000,000            │
│  • gate_count ≤ 100000                                          │
│  • qubits ≥ 2                                                   │
│                                                                  │
│  ┌─── Neither compatible? ──▶ REJECT                            │
│  └─── Only one compatible? ──▶ FORCE that hardware (Step 3)     │
└──────────────────────┬───────────────────────────────────────────┘
                       │ both compatible
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 2: Safety Constraints                                       │
│                                                                  │
│  • Circuit volume (qubits × depth) ≤ 1,000,000                  │
│  • Noise sensitivity (qubits × depth × cx_ratio) ≤ 50,000       │
│  • NISQ viability P(success) ≥ 0.01                              │
│      P(success) = P(gates) × P(readout) × P(decoherence)        │
│      ├─ P(gates)       = (1-e_2q)^n_2q × (1-e_1q)^n_1q         │
│      ├─ P(readout)     = (1-e_ro)^n_qubits                      │
│      └─ P(decoherence) = exp(-circuit_time / T2)                 │
│                                                                  │
│  Uses live IBM device calibration from HAL:                      │
│    median_cx_error, median_sx_error, median_readout_error,       │
│    median_t2_us, median_gate_time_ns                             │
│                                                                  │
│  Exception: if qubits > 40, classical sim is infeasible          │
│  (2^40+ amplitudes) so quantum is allowed despite low viability  │
│                                                                  │
│  ┌─── Violated? ──▶ FORCE_CLASSICAL                             │
└──┴───────────────────┬───────────────────────────────────────────┘
                       │ safe
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 3: Clear-Cut Rules                                          │
│                                                                  │
│  • Only quantum compatible?  ──▶ FORCE_QUANTUM                   │
│  • Only classical compatible? ──▶ FORCE_CLASSICAL                │
│  • problem_size < 10 AND qubits < 5? ──▶ FORCE_CLASSICAL        │
│    (too small for quantum overhead)                              │
│  • qubits == 0 OR (superposition < 0.1 AND entanglement < 0.1)  │
│    ──▶ FORCE_CLASSICAL (no quantum features)                     │
│                                                                  │
│  ┌─── Rule matched? ──▶ Return forced decision                  │
└──┴───────────────────┬───────────────────────────────────────────┘
                       │ no clear-cut rule
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 4: Quantum Advantage Threshold                              │
│                                                                  │
│  Feature Score (weighted):                                       │
│    score = superposition×0.4 + entanglement×0.4 + cx_ratio×0.2  │
│                                                                  │
│  Strong features? (need ONE of):                                 │
│    • score ≥ 0.65                                                │
│    • 3+ indicators met:                                          │
│        - superposition ≥ 0.6                                     │
│        - entanglement ≥ 0.5                                      │
│        - cx_gate_ratio ≥ 0.2                                     │
│        - EXPONENTIAL complexity                                  │
│        - QUADRATIC_SPEEDUP complexity                            │
│                                                                  │
│  Practical scale? (need ONE of):                                 │
│    • qubits ≥ 20  (classical sim becomes expensive)              │
│    • problem_size ≥ 500 AND complexity is                        │
│      EXPONENTIAL or QUADRATIC_SPEEDUP                            │
│                                                                  │
│  ┌─── Strong features AND practical scale?                       │
│  │    ──▶ FORCE_QUANTUM                                          │
│  └─── Otherwise: continue (features noted but no override)       │
└──────────────────────┬───────────────────────────────────────────┘
                       │ no quantum advantage
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 5: Problem-Type Routing                                     │
│                                                                  │
│  Problem Type       Preferred    Reason                          │
│  ─────────────────  ──────────   ─────────────────────────────── │
│  FACTORIZATION      Quantum      Shor's algorithm (exp speedup)  │
│  SEARCH             Quantum      Grover's (quadratic speedup)    │
│  SIMULATION         Quantum      Natural quantum simulation      │
│  OPTIMIZATION       Quantum      QAOA/VQE exploration            │
│  SORTING            Classical    Classical sorting is optimal     │
│  DYNAMIC_PROG       Classical    Sequential dependencies         │
│  MATRIX_OPS         Classical    Mature classical libraries       │
│                                                                  │
│  Quantum-preferred types also require:                           │
│    • Minimum qubits: FACTOR ≥ 8, SEARCH ≥ 4, SIM ≥ 6, OPT ≥ 6 │
│    • Practical scale: qubits ≥ 20 to FORCE quantum              │
│      (< 20 qubits → ALLOW_BOTH, defer to weighted merger)       │
│                                                                  │
│  Classical-preferred types always FORCE_CLASSICAL                 │
│                                                                  │
│  ┌─── Quantum + large scale? ──▶ FORCE_QUANTUM                  │
│  ├─── Quantum + small scale? ──▶ ALLOW_BOTH (defer to merger)   │
│  ├─── Classical preferred?   ──▶ FORCE_CLASSICAL                 │
│  └─── No match?             ──▶ continue to Step 6              │
└──────────────────────┬───────────────────────────────────────────┘
                       │ no problem-specific rule
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 6: Default — ALLOW_BOTH                                     │
│                                                                  │
│  No rule applies. Return decision_type = ALLOW_BOTH              │
│  ──▶ Defer to weighted merger (ML 50% + Rules 35% + Cost 15%)   │
└──────────────────────────────────────────────────────────────────┘
```

## Decision Merger Flow

```
                    Rule Decision
                        │
                        ▼
              ┌─────────────────────┐
              │  FORCE_QUANTUM or   │──── yes ──▶ Return rule override
              │  FORCE_CLASSICAL or │             (bypasses all scoring)
              │  REJECT?            │
              └─────────┬───────────┘
                        │ no (ALLOW_BOTH)
                        ▼
              ┌─────────────────────┐
              │  Weighted Scoring   │
              │                     │
              │  For each hardware: │
              │  ┌────────────────┐ │
              │  │ ML score:      │ │
              │  │  conf × 0.50   │ │
              │  ├────────────────┤ │
              │  │ Rule score:    │ │
              │  │  conf × 0.35   │ │
              │  │  (0.175 each   │ │
              │  │  if ALLOW_BOTH)│ │
              │  ├────────────────┤ │
              │  │ Cost score:    │ │
              │  │  0.15 if       │ │
              │  │  cost-optimal  │ │
              │  │  +0.05 bonus   │ │
              │  │  if agrees     │ │
              │  │  with ML       │ │
              │  └────────────────┘ │
              │                     │
              │  total = sum(above) │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │  Highest total wins │
              │  (tie → Classical)  │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │  Build rationale    │
              │  from all 3 sources │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ HardwareRecommend.  │
              │  • hardware         │
              │  • confidence       │
              │  • quantum_prob     │
              │  • classical_prob   │
              │  • rationale        │
              └─────────────────────┘
```

## Cost Analyzer Formulas

```
QUANTUM TIME:
  base_circuit_time  = circuit_depth × 0.1ms
  gate_time          = gate_count × 0.05ms
  shot_overhead      = 1024 shots × 0.01ms
  × problem_type_overhead (0.9–1.5)
  × complexity_multiplier (0.5–2.0)
  × NISQ_overhead (1.2)
  + queue_time (50–500ms by qubit count)

QUANTUM COST:
  $0.30 base/task
  + 1024 × $0.00145/shot
  + (time_ms/1000) × $1.60/sec
  + gate_count × $0.0001/gate

CLASSICAL TIME:
  EXPONENTIAL:  problem_size² × 0.1ms
  POLYNOMIAL:   problem_size^1.5 × 0.05ms
  NLOGN:        problem_size × log₂(size) × 0.01ms
  DEFAULT:      problem_size × 0.1ms
  + memory_mb × 0.01ms
  × problem_type_multiplier (0.5–5.0)

CLASSICAL COST:
  (time_ms/1000) × $0.0001/sec
  + (memory_gb) × (time_ms/1000) × $0.00001/GB·s
  + $0.001 overhead
```
