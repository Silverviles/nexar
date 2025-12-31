# Decision Engine: Technical Documentation
## How Predictions, Costs, and Decision-Making Work

---

## Table of Contents
1. [Overview](#overview)
2. [Architecture & Data Flow](#architecture--data-flow)
3. [Component Deep Dive](#component-deep-dive)
4. [Prediction System](#prediction-system)
5. [Cost Analysis](#cost-analysis)
6. [Decision Merging](#decision-merging)
7. [Examples](#examples)

---

## Overview

The **Decision Engine** is the brain of the Nexar system. It takes code analysis data and determines whether quantum or classical hardware is optimal for execution. The engine uses a **hybrid approach** combining:

- **Machine Learning (50% weight)**: Neural network trained on 10,000+ problem instances
- **Rule-Based System (35% weight)**: Physics-aware constraints and safety checks
- **Cost Analysis (15% weight)**: Real-time execution time and cost predictions

### Key Metrics
- **Input**: 16 features describing problem characteristics
- **Output**: Hardware recommendation (Quantum/Classical) with confidence score
- **Processing Time**: ~50-100ms per prediction
- **Accuracy**: ~87% on test data

---

## Architecture & Data Flow

```
Input: Code Analysis Data
         |
         v
    ┌─────────────────────────────────┐
    │   Decision Engine Service       │
    └─────────────────────────────────┘
                  |
      ┌───────────┴───────────┬───────────────┐
      v                       v               v
┌──────────┐          ┌──────────┐     ┌──────────┐
│ ML Model │          │  Rules   │     │   Cost   │
│ (50%)    │          │  (35%)   │     │  (15%)   │
└──────────┘          └──────────┘     └──────────┘
      |                       |               |
      └───────────┬───────────┴───────────────┘
                  v
         ┌────────────────┐
         │ Decision Merger│
         └────────────────┘
                  |
                  v
         Final Recommendation
         + Cost Estimates
         + Alternatives
```

### Processing Pipeline

1. **Feature Preparation**: Convert raw code metrics into 16-feature vector
2. **ML Prediction**: Neural network predicts hardware with confidence
3. **Rule Evaluation**: Physics-aware validation and safety checks
4. **Cost Analysis**: Calculate execution time and cost for both options
5. **Decision Merging**: Weighted voting to determine final recommendation
6. **Response Construction**: Package recommendation with alternatives and estimates

---

## Component Deep Dive

### 1. ML Model Prediction

**Purpose**: Learn patterns from historical data to predict optimal hardware

**Model Architecture**:
- Type: Random Forest / Neural Network (configurable)
- Training Data: 10,000+ synthetic problem instances
- Features: 16 total (10 raw + 6 derived physics features)
- Output: Binary classification (Quantum=1, Classical=0)

**Input Features (16 total)**:

**Raw Features (10)**:
1. `problem_size` - Number of elements/variables
2. `qubits_required` - Quantum bits needed
3. `circuit_depth` - Quantum gate layers
4. `gate_count` - Total quantum gates
5. `cx_gate_ratio` - Ratio of entangling gates (0-1)
6. `superposition_score` - Superposition potential (0-1)
7. `entanglement_score` - Entanglement potential (0-1)
8. `memory_requirement_mb` - RAM needed
9. `problem_type_encoded` - Category: factorization, search, etc.
10. `time_complexity_encoded` - Complexity class: exponential, polynomial, etc.

**Derived Physics Features (6)**:
11. `circuit_volume` = `qubits_required × circuit_depth`
    - Measures quantum resource intensity
    - High volume → more susceptible to noise

12. `noise_sensitivity` = `qubits_required × circuit_depth × cx_gate_ratio`
    - Predicts error accumulation
    - CNOT gates are major error source

13. `quantum_overhead_ratio` = `problem_size / qubits_required`
    - Efficiency of quantum encoding
    - Lower is better (dense encoding)

14. `nisq_viability_score` - Composite viability metric
    - Penalized if: qubits > 50, depth > 1000, or volume > 50,000
    - Score of 0.1 means problem is at NISQ limits

15. `gate_density` = `gate_count / qubits_required`
    - Gates per qubit
    - Higher density → more complex operations

16. `entanglement_factor` = `cx_gate_ratio × entanglement_score`
    - Combined entanglement potential
    - Key indicator for quantum advantage

**Prediction Process**:
```python
# 1. Encode categorical features
problem_type_encoded = encode(problem_type)
time_complexity_encoded = encode(time_complexity)

# 2. Calculate physics features
circuit_volume = qubits × depth
noise_sensitivity = qubits × depth × cx_ratio
# ... other derived features

# 3. Create feature vector [16 elements]
features = [raw_features..., physics_features...]

# 4. Scale features (standardization)
scaled_features = scaler.transform(features)

# 5. Make prediction
probabilities = model.predict_proba(scaled_features)
quantum_prob = probabilities[1]
classical_prob = probabilities[0]
confidence = max(quantum_prob, classical_prob)

# 6. Determine recommendation
if quantum_prob > classical_prob:
    hardware = "Quantum"
else:
    hardware = "Classical"
```

**ML Decision Output**:
```json
{
  "hardware": "Quantum",
  "confidence": 0.87,
  "quantum_probability": 0.87,
  "classical_probability": 0.13,
  "rationale": "ML Model predicts Quantum with 87.0% confidence"
}
```

---

### 2. Rule-Based System

**Purpose**: Enforce physics constraints, safety limits, and deterministic routing rules

**Rule Categories**:

#### A. Hardware Capability Constraints
```python
quantum_limits = {
    'max_qubits': 127,        # IBM Quantum Eagle
    'max_circuit_depth': 10000,
    'max_gate_count': 100000,
    'min_qubits': 2
}

classical_limits = {
    'max_memory_gb': 512,
    'max_problem_size': 1000000
}
```

#### B. Quantum Advantage Thresholds
Problems must meet minimum quantum characteristics:
- `superposition_score >= 0.6`
- `entanglement_score >= 0.5`
- `cx_gate_ratio >= 0.2`
- Combined quantum score >= 0.65

#### C. Problem-Type Routing Rules

**Quantum-Favorable Problems**:
- **Factorization**: Shor's algorithm provides exponential speedup
  - Min qubits: 8
  - Rule: FORCE_QUANTUM if qubits available
  
- **Search**: Grover's algorithm offers quadratic speedup
  - Min qubits: 4
  - Rule: Prefer quantum for large search spaces
  
- **Simulation**: Quantum systems naturally simulate quantum phenomena
  - Min qubits: 6
  - Rule: Strong quantum preference
  
- **Optimization**: QAOA/VQE can explore solution space efficiently
  - Min qubits: 6
  - Rule: Quantum beneficial for complex landscapes

**Classical-Favorable Problems**:
- **Sorting**: Classical algorithms highly optimized (O(n log n))
  - Rule: FORCE_CLASSICAL
  
- **Dynamic Programming**: Sequential dependencies limit quantum parallelism
  - Rule: FORCE_CLASSICAL
  
- **Matrix Operations**: Classical linear algebra libraries mature
  - Rule: Classical unless problem size > 10,000

#### D. Safety Constraints
Prevent execution that would fail:
```python
safety_rules = {
    'max_circuit_volume': 1000000,     # qubits × depth
    'max_noise_sensitivity': 50000,    # Risk of decoherence
    'min_nisq_viability': 0.1          # Minimum feasibility
}
```

**Rule Evaluation Process**:
```python
# Step 1: Check hardware compatibility
if qubits_required > quantum_limits['max_qubits']:
    quantum_compatible = False

if memory_requirement > classical_limits['max_memory_gb']:
    classical_compatible = False

# Step 2: Check safety constraints
circuit_volume = qubits × depth
if circuit_volume > safety_rules['max_circuit_volume']:
    return REJECT  # Too risky to execute

# Step 3: Apply problem-type rules
if problem_type == "factorization" and qubits >= 8:
    return FORCE_QUANTUM
    
if problem_type == "sorting":
    return FORCE_CLASSICAL

# Step 4: Calculate quantum advantage score
quantum_score = (
    0.3 × superposition_score +
    0.3 × entanglement_score +
    0.2 × cx_gate_ratio +
    0.2 × (1 - noise_sensitivity_normalized)
)

if quantum_score >= 0.65:
    return ALLOW_QUANTUM  # Strong quantum characteristics
else:
    return PREFER_CLASSICAL
```

**Rule Decision Types**:
- `FORCE_QUANTUM`: Rules mandate quantum (overrides ML)
- `FORCE_CLASSICAL`: Rules mandate classical (overrides ML)
- `ALLOW_BOTH`: No strong preference, use ML + cost
- `REJECT`: Problem cannot be executed safely

**Rule Decision Output**:
```json
{
  "decision_type": "ALLOW_BOTH",
  "hardware": "Quantum",
  "confidence": 0.75,
  "quantum_advantage_score": 0.68,
  "rationale": "High superposition and entanglement scores indicate quantum advantage"
}
```

---

### 3. Cost Analysis

**Purpose**: Calculate execution time and monetary cost for quantum vs classical

#### A. Pricing Models

**Quantum Hardware Pricing** (based on real providers):
```python
quantum_pricing = {
    'base_cost_per_task': 0.30,      # $0.30 per job submission
    'cost_per_shot': 0.00145,        # $0.00145 per measurement
    'cost_per_second': 1.60,         # $1.60 per second QPU time
    'default_shots': 1024,           # Standard for reliability
    'cost_per_gate': 0.0001,         # ~$0.0001 per gate
}
```

**Classical Hardware Pricing** (AWS EC2 approximation):
```python
classical_pricing = {
    'cost_per_second': 0.0001,       # ~$0.36/hour
    'cost_per_gb_memory': 0.00001,   # Memory overhead
    'base_overhead': 0.001,          # Job setup
}
```

#### B. Execution Time Estimation

**Quantum Time Calculation**:
```python
def estimate_quantum_time(input_data):
    # Base circuit execution time
    base_circuit_time = circuit_depth × 0.1 ms  # ~100ns per layer
    gate_execution_time = gate_count × 0.05 ms  # ~50ns per gate
    shot_overhead = 1024 × 0.01 ms              # Measurement time
    
    # Problem-specific overhead
    problem_overhead = {
        'factorization': 1.5,
        'search': 1.3,
        'optimization': 1.4,
        'sorting': 1.0,
    }[problem_type]
    
    # Complexity multiplier
    complexity_mult = {
        'exponential': 2.0,
        'polynomial': 1.5,
        'polynomial_speedup': 0.8,
    }[time_complexity]
    
    # NISQ hardware overhead (calibration, error mitigation)
    nisq_overhead = 1.2  # 20% overhead
    
    # Total time
    total_time = (base_circuit_time + gate_execution_time + shot_overhead) \
                 × problem_overhead × complexity_mult × nisq_overhead
    
    # Add queue time (varies by provider load)
    queue_time = estimate_queue_time(qubits_required)
    
    return total_time + queue_time
```

**Classical Time Calculation**:
```python
def estimate_classical_time(input_data):
    # Base computation (problem size dependent)
    if time_complexity == 'exponential':
        base_time = problem_size ** 2 × 0.1 ms
    elif time_complexity == 'polynomial':
        base_time = problem_size ** 1.5 × 0.05 ms
    elif time_complexity == 'nlogn':
        base_time = problem_size × log2(problem_size) × 0.01 ms
    
    # Memory access overhead
    memory_overhead = memory_requirement_mb × 0.01 ms
    
    # Problem-specific multiplier
    problem_mult = {
        'factorization': 5.0,   # Very slow classically
        'search': 2.0,          # Linear vs quadratic
        'sorting': 0.5,         # Fast classically
    }[problem_type]
    
    return (base_time + memory_overhead) × problem_mult
```

#### C. Cost Calculation

**Quantum Cost**:
```python
def calculate_quantum_cost(input_data, quantum_time_ms):
    # Job submission fee
    base_cost = quantum_pricing['base_cost_per_task']  # $0.30
    
    # QPU usage time
    qpu_time_cost = (quantum_time_ms / 1000) × quantum_pricing['cost_per_second']
    
    # Measurement shots
    shot_cost = quantum_pricing['default_shots'] × quantum_pricing['cost_per_shot']
    
    # Gate execution cost
    gate_cost = gate_count × quantum_pricing['cost_per_gate']
    
    # Total quantum cost
    total_cost = base_cost + qpu_time_cost + shot_cost + gate_cost
    
    return total_cost
```

**Classical Cost**:
```python
def calculate_classical_cost(input_data, classical_time_ms):
    # Compute time cost
    compute_cost = (classical_time_ms / 1000) × classical_pricing['cost_per_second']
    
    # Memory cost
    memory_gb = memory_requirement_mb / 1024
    memory_cost = memory_gb × (classical_time_ms / 1000) × classical_pricing['cost_per_gb_memory']
    
    # Base overhead
    overhead_cost = classical_pricing['base_overhead']
    
    # Total classical cost
    total_cost = compute_cost + memory_cost + overhead_cost
    
    return total_cost
```

#### D. ROI Analysis

```python
def calculate_roi(quantum_cost, classical_cost, quantum_time, classical_time):
    # Cost savings
    cost_savings = classical_cost - quantum_cost
    
    # Time savings (in ms)
    time_savings = classical_time - quantum_time
    
    # ROI percentage
    if quantum_cost > 0:
        roi = (cost_savings / quantum_cost) × 100
    else:
        roi = 0
    
    # Speedup factor
    speedup = classical_time / max(quantum_time, 1)
    
    return {
        'roi': roi,
        'cost_savings': cost_savings,
        'time_savings': time_savings,
        'speedup_factor': speedup
    }
```

**Cost Analysis Output**:
```json
{
  "quantum_time_ms": 1500.0,
  "classical_time_ms": 8500.0,
  "time_speedup_factor": 5.67,
  
  "quantum_cost_usd": 0.25,
  "classical_cost_usd": 0.12,
  "cost_difference_usd": 0.13,
  
  "roi_quantum_vs_classical": -52.0,
  "cost_per_ms_quantum": 0.000167,
  "cost_per_ms_classical": 0.000014,
  
  "quantum_within_budget": true,
  "classical_within_budget": true,
  
  "cost_optimal_hardware": "Classical",
  "ml_suggestion": "Quantum",
  "cost_agrees_with_ml": false
}
```

---

### 4. Decision Merging

**Purpose**: Combine ML predictions, rules, and cost analysis into final recommendation

#### A. Weighting Strategy

```python
decision_weights = {
    'ml_model': 0.50,        # 50% weight to ML predictions
    'rule_system': 0.35,     # 35% weight to physics rules
    'cost_analysis': 0.15,   # 15% weight to cost optimization
}
```

#### B. Merging Algorithm

```python
def merge_decisions(ml_decision, rule_decision, cost_analysis):
    # STEP 1: Check for rule overrides (highest priority)
    if rule_decision['decision_type'] == 'FORCE_QUANTUM':
        return create_override_recommendation('Quantum', rule_decision)
    
    if rule_decision['decision_type'] == 'FORCE_CLASSICAL':
        return create_override_recommendation('Classical', rule_decision)
    
    if rule_decision['decision_type'] == 'REJECT':
        return create_rejection_recommendation(rule_decision)
    
    # STEP 2: Calculate weighted scores for each hardware option
    scores = {
        'Quantum': {'ml': 0, 'rule': 0, 'cost': 0, 'total': 0},
        'Classical': {'ml': 0, 'rule': 0, 'cost': 0, 'total': 0}
    }
    
    # ML contribution
    if ml_decision['hardware'] == 'Quantum':
        scores['Quantum']['ml'] = ml_decision['confidence'] × 0.50
        scores['Classical']['ml'] = (1 - ml_decision['confidence']) × 0.50
    else:
        scores['Classical']['ml'] = ml_decision['confidence'] × 0.50
        scores['Quantum']['ml'] = (1 - ml_decision['confidence']) × 0.50
    
    # Rule contribution
    if rule_decision['hardware'] == 'Quantum':
        scores['Quantum']['rule'] = rule_decision['confidence'] × 0.35
        scores['Classical']['rule'] = (1 - rule_decision['confidence']) × 0.35
    elif rule_decision['hardware'] == 'Classical':
        scores['Classical']['rule'] = rule_decision['confidence'] × 0.35
        scores['Quantum']['rule'] = (1 - rule_decision['confidence']) × 0.35
    else:  # ALLOW_BOTH
        # Split rule weight evenly
        scores['Quantum']['rule'] = 0.175
        scores['Classical']['rule'] = 0.175
    
    # Cost contribution
    cost_optimal = cost_analysis['cost_optimal_hardware']
    if cost_optimal == 'Quantum':
        scores['Quantum']['cost'] = 0.15
        scores['Classical']['cost'] = 0.0
    else:
        scores['Classical']['cost'] = 0.15
        scores['Quantum']['cost'] = 0.0
    
    # STEP 3: Calculate total scores
    scores['Quantum']['total'] = sum([
        scores['Quantum']['ml'],
        scores['Quantum']['rule'],
        scores['Quantum']['cost']
    ])
    
    scores['Classical']['total'] = sum([
        scores['Classical']['ml'],
        scores['Classical']['rule'],
        scores['Classical']['cost']
    ])
    
    # STEP 4: Select hardware with highest score
    if scores['Quantum']['total'] > scores['Classical']['total']:
        final_hardware = 'Quantum'
        final_confidence = scores['Quantum']['total']
    else:
        final_hardware = 'Classical'
        final_confidence = scores['Classical']['total']
    
    # STEP 5: Build comprehensive rationale
    rationale = build_rationale(
        final_hardware, ml_decision, rule_decision, 
        cost_analysis, scores
    )
    
    return HardwareRecommendation(
        recommended_hardware=final_hardware,
        confidence=final_confidence,
        quantum_probability=ml_decision['quantum_probability'],
        classical_probability=ml_decision['classical_probability'],
        rationale=rationale
    )
```

#### C. Rationale Construction

```python
def build_rationale(final_hw, ml_decision, rule_decision, cost_analysis, scores):
    parts = []
    
    # ML component
    ml_agrees = (ml_decision['hardware'] == final_hw)
    parts.append(f"ML model {'supports' if ml_agrees else 'differs from'} "
                f"this decision (confidence: {ml_decision['confidence']:.1%})")
    
    # Rule component
    if rule_decision['hardware'] == final_hw:
        parts.append(f"Rules favor {final_hw}: {rule_decision['rationale']}")
    
    # Cost component
    cost_agrees = (cost_analysis['cost_optimal_hardware'] == final_hw)
    if cost_agrees:
        parts.append(f"Cost analysis supports {final_hw}")
    else:
        alt_hw = 'Classical' if final_hw == 'Quantum' else 'Quantum'
        cost_diff = cost_analysis['cost_difference_usd']
        parts.append(f"{alt_hw} is ${cost_diff:.4f} cheaper, but performance "
                    f"benefit justifies {final_hw}")
    
    # Performance metrics
    if final_hw == 'Quantum':
        speedup = cost_analysis['time_speedup_factor']
        parts.append(f"Expected {speedup:.1f}x speedup over classical")
    
    # Confidence assessment
    if scores[final_hw]['total'] > 0.85:
        parts.append("High confidence decision")
    elif scores[final_hw]['total'] > 0.65:
        parts.append("Moderate confidence")
    else:
        parts.append("Low confidence - consider alternatives")
    
    return ". ".join(parts) + "."
```

**Example Merged Decision**:
```json
{
  "recommended_hardware": "Quantum",
  "confidence": 0.79,
  "quantum_probability": 0.87,
  "classical_probability": 0.13,
  "rationale": "ML model supports this decision (confidence: 87.0%). Rules favor Quantum: High superposition and entanglement scores indicate quantum advantage. Classical is $0.1300 cheaper, but performance benefit justifies Quantum. Expected 5.7x speedup over classical. Moderate confidence."
}
```

---

## Complete Processing Example

### Input
```json
{
  "problem_type": "optimization",
  "problem_size": 500,
  "qubits_required": 12,
  "circuit_depth": 150,
  "gate_count": 500,
  "cx_gate_ratio": 0.33,
  "superposition_score": 0.75,
  "entanglement_score": 0.70,
  "time_complexity": "polynomial_speedup",
  "memory_requirement_mb": 200.0
}
```

### Step-by-Step Processing

**1. Feature Preparation**
```python
raw_features = [500, 12, 150, 500, 0.33, 0.75, 0.70, 200.0, 3, 3]
physics_features = [
    1800,      # circuit_volume = 12 × 150
    594,       # noise_sensitivity = 12 × 150 × 0.33
    41.67,     # quantum_overhead_ratio = 500 / 12
    1.0,       # nisq_viability_score (good parameters)
    41.67,     # gate_density = 500 / 12
    0.231      # entanglement_factor = 0.33 × 0.70
]
feature_vector = raw_features + physics_features  # 16 features
```

**2. ML Prediction**
```json
{
  "hardware": "Quantum",
  "confidence": 0.87,
  "quantum_probability": 0.87,
  "classical_probability": 0.13
}
```

**3. Rule Evaluation**
```json
{
  "decision_type": "ALLOW_BOTH",
  "hardware": "Quantum",
  "confidence": 0.75,
  "quantum_advantage_score": 0.68,
  "rationale": "High superposition (0.75) and entanglement (0.70) scores"
}
```

**4. Cost Analysis**
```json
{
  "quantum_time_ms": 1500.0,
  "classical_time_ms": 8500.0,
  "quantum_cost_usd": 0.25,
  "classical_cost_usd": 0.12,
  "cost_optimal_hardware": "Classical",
  "time_speedup_factor": 5.67
}
```

**5. Decision Merging**
```python
scores = {
    'Quantum': {
        'ml': 0.87 × 0.50 = 0.435,
        'rule': 0.75 × 0.35 = 0.263,
        'cost': 0.0,  # Classical is cheaper
        'total': 0.698
    },
    'Classical': {
        'ml': 0.13 × 0.50 = 0.065,
        'rule': 0.25 × 0.35 = 0.088,
        'cost': 0.15,  # Cost optimal
        'total': 0.303
    }
}

final_decision = 'Quantum' (score: 0.698 > 0.303)
```

**6. Final Response**
```json
{
  "success": true,
  "recommendation": {
    "recommended_hardware": "Quantum",
    "confidence": 0.70,
    "quantum_probability": 0.87,
    "classical_probability": 0.13,
    "rationale": "ML model supports this decision (confidence: 87.0%). Rules favor Quantum: High superposition and entanglement scores indicate quantum advantage. Classical is $0.1300 cheaper, but performance benefit justifies Quantum. Expected 5.7x speedup over classical. Moderate confidence."
  },
  "alternatives": [
    {
      "hardware": "Classical",
      "confidence": 0.30,
      "trade_off": "Alternative: 8500ms execution, $0.1200 cost"
    }
  ],
  "estimated_execution_time_ms": 1500.0,
  "estimated_cost_usd": 0.25,
  "error": null
}
```

---

## Key Insights

### When Quantum is Recommended
1. **High ML Confidence** (>0.80) for quantum
2. **Strong Quantum Characteristics**:
   - Superposition score > 0.6
   - Entanglement score > 0.5
   - Good NISQ viability (qubits < 50, depth < 1000)
3. **Problem Type**: Factorization, search, simulation, optimization
4. **Performance Gain** outweighs cost difference

### When Classical is Recommended
1. **High ML Confidence** (>0.80) for classical
2. **Weak Quantum Characteristics**:
   - Low superposition/entanglement scores
   - Poor NISQ viability (too many qubits, too deep)
3. **Problem Type**: Sorting, dynamic programming, matrix ops
4. **Cost-Effective**: Significantly cheaper with acceptable performance

### When Rules Override ML
1. **Safety Constraints Violated**: Circuit volume > 1,000,000
2. **Hardware Incompatibility**: Qubits > 127 (IBM limit)
3. **Problem Type Mandates**: Sorting always goes to classical
4. **Physical Impossibility**: Problem cannot be executed quantum-mechanically

### Cost Considerations
- **Quantum is 10-100x more expensive** per second
- **But** can be 2-10x faster for suitable problems
- **ROI** is positive when: speedup_factor × time_saved > cost_increase
- **Budget constraints** can force classical even when quantum is better

---

## Performance Characteristics

### Typical Latency
- Feature preparation: 5-10ms
- ML inference: 20-30ms
- Rule evaluation: 5-10ms
- Cost analysis: 10-15ms
- Decision merging: 5-10ms
- **Total**: 50-100ms per prediction

### Accuracy Metrics (Test Set)
- **Overall Accuracy**: 87%
- **Quantum Precision**: 89%
- **Classical Precision**: 85%
- **False Positive Rate** (Classical as Quantum): 8%
- **False Negative Rate** (Quantum as Classical): 15%

### Cost Prediction Accuracy
- **Time Estimation Error**: ±20-30% (highly variable due to queue times)
- **Cost Estimation Error**: ±10-15%
- **ROI Calculation**: Directionally correct, not precise

---

## Configuration & Tuning

### Adjusting Decision Weights
Edit `decision_merger.py`:
```python
self.decision_weights = {
    'ml_model': 0.50,        # Increase for more data-driven decisions
    'rule_system': 0.35,     # Increase for more conservative decisions
    'cost_analysis': 0.15,   # Increase for more cost-conscious decisions
}
```

### Modifying Pricing Models
Edit `cost_analyser.py`:
```python
self.quantum_pricing = {
    'base_cost_per_task': 0.30,  # Adjust based on provider
    'cost_per_second': 1.60,     # Update with real QPU costs
    # ...
}
```

### Changing Rule Thresholds
Edit `rule_service.py`:
```python
self.quantum_advantage_thresholds = {
    'min_superposition_score': 0.6,  # Lower = more lenient
    'min_entanglement_score': 0.5,
    # ...
}
```

---

## Common Questions

**Q: Why does the engine recommend quantum even though it's more expensive?**
A: Performance benefit (speedup) outweighs cost difference. The engine optimizes for execution time when the cost difference is reasonable (<2x).

**Q: Can I force the engine to always choose the cheapest option?**
A: Yes, increase the `cost_analysis` weight to 0.50+ in `decision_weights`.

**Q: How accurate are the cost predictions?**
A: Time estimates have ±20-30% error, cost estimates ±10-15%. These are directional, not precise quotes.

**Q: What happens if both quantum and classical are incompatible?**
A: The engine returns `decision_type: REJECT` with a rationale explaining the limitation.

**Q: Can I retrain the ML model?**
A: Yes, the model is stored in `ml_models/decision_engine_model.pkl`. Retrain using the Jupyter notebook and replace the model file.

---

## Monitoring & Debugging

### Enable Detailed Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Key Log Messages
- `"Evaluating rules for {problem_type} problem"`
- `"ML model predicts {hardware} with {confidence:.1%} confidence"`
- `"Cost Analysis: Q=${quantum_cost:.4f} vs C=${classical_cost:.4f}"`
- `"Final Decision: {hardware} (confidence: {confidence:.2%})"`

### Health Check Endpoint
```bash
curl http://localhost:8083/api/v1/decision-engine/health
```

Response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_type": "RandomForestClassifier",
  "model_accuracy": 0.87
}
```

---

## Summary

The Decision Engine is a **sophisticated multi-component system** that combines:

1. **Data-driven ML predictions** (87% accuracy)
2. **Physics-aware rule validation** (safety and compatibility)
3. **Economic cost-benefit analysis** (real-time pricing)

The system processes decisions in **~50-100ms** and provides:
- Hardware recommendation (Quantum/Classical)
- Confidence score (0-1)
- Cost estimates (USD)
- Execution time estimates (ms)
- Alternative options with trade-offs
- Detailed rationale explaining the decision

This hybrid approach ensures **safe, cost-effective, and performant** hardware allocation for quantum-classical workload distribution.
