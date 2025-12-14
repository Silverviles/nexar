"""
Cost Analyzer Component for Decision Engine
Performs real-time cost analysis, execution time prediction, and ROI calculations
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime

try:
    from ..schemas.decision_engine import (
        CodeAnalysisInput,
        HardwareType,
        ProblemType,
        TimeComplexity
    )
except ImportError:
    from schemas.decision_engine import (
        CodeAnalysisInput,
        HardwareType,
        ProblemType,
        TimeComplexity
    )

logger = logging.getLogger(__name__)


class CostAnalyzer:
    """
    Analyzes costs and execution times for quantum vs classical hardware.
    Implements cost-benefit analysis as per research objectives SO3.
    """
    
    def __init__(self):
        """Initialize cost analyzer with pricing models"""
        
        # ---------------------------------------------------------
        # QUANTUM HARDWARE PRICING (Based on real provider costs)
        # ---------------------------------------------------------
        # IBM Quantum: ~$1.60 per second
        # Amazon Braket: ~$0.30 per task + $0.00145 per shot
        # These are realistic approximations for NISQ-era quantum systems
        
        self.quantum_pricing = {
            'base_cost_per_task': 0.30,  # USD per quantum job submission
            'cost_per_shot': 0.00145,    # USD per measurement shot
            'cost_per_second': 1.60,     # USD per second of QPU time
            'default_shots': 1024,       # Standard shot count for reliable results
            'cost_per_gate': 0.0001,     # Approximate cost per quantum gate
        }
        
        # ---------------------------------------------------------
        # CLASSICAL HARDWARE PRICING (Cloud compute approximation)
        # ---------------------------------------------------------
        # Based on AWS EC2 pricing for high-performance instances
        # c6i.2xlarge: ~$0.34/hour = ~$0.0000944/second
        
        self.classical_pricing = {
            'cost_per_second': 0.0001,   # USD per second of compute
            'cost_per_gb_memory': 0.00001,  # USD per GB-second
            'base_overhead': 0.001,      # Small overhead per task
        }
        
        # ---------------------------------------------------------
        # EXECUTION TIME MODELS
        # ---------------------------------------------------------
        # These multipliers adjust base execution time based on problem characteristics
        
        self.time_complexity_multipliers = {
            TimeComplexity.EXPONENTIAL: 2.0,
            TimeComplexity.POLYNOMIAL: 1.5,
            TimeComplexity.POLYNOMIAL_SPEEDUP: 0.8,
            TimeComplexity.QUADRATIC_SPEEDUP: 0.5,
            TimeComplexity.NLOGN: 1.2,
        }
        
        self.problem_type_overhead = {
            ProblemType.FACTORIZATION: 1.5,      # High quantum advantage
            ProblemType.SEARCH: 1.3,             # Grover's speedup
            ProblemType.SIMULATION: 1.2,         # Natural quantum problem
            ProblemType.OPTIMIZATION: 1.4,       # QAOA/VQE overhead
            ProblemType.SORTING: 1.0,            # Better on classical
            ProblemType.DYNAMIC_PROGRAMMING: 0.9,
            ProblemType.MATRIX_OPS: 1.1,
            ProblemType.RANDOM_CIRCUIT: 1.0,
        }

    def analyze(
        self, 
        input_data: CodeAnalysisInput, 
        ml_hardware_suggestion: HardwareType,
        budget_limit_usd: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive cost-benefit analysis
        
        Args:
            input_data: Code analysis input containing problem characteristics
            ml_hardware_suggestion: Hardware suggested by ML model
            budget_limit_usd: Optional budget constraint
            
        Returns:
            Dictionary containing cost analysis results
        """
        
        # Calculate execution times
        quantum_time_ms = self._estimate_quantum_time(input_data)
        classical_time_ms = self._estimate_classical_time(input_data)
        
        # Calculate costs
        quantum_cost_usd = self._calculate_quantum_cost(input_data, quantum_time_ms)
        classical_cost_usd = self._calculate_classical_cost(input_data, classical_time_ms)
        
        # ROI Analysis
        roi_analysis = self._calculate_roi(
            quantum_cost_usd, classical_cost_usd,
            quantum_time_ms, classical_time_ms
        )
        
        # Budget validation
        budget_status = self._check_budget_constraints(
            quantum_cost_usd, 
            classical_cost_usd,
            budget_limit_usd
        )
        
        # Cost-benefit recommendation
        cost_optimal_hardware = self._determine_cost_optimal_hardware(
            quantum_cost_usd, classical_cost_usd,
            quantum_time_ms, classical_time_ms,
            input_data
        )
        
        analysis_result = {
            # Time estimates
            'quantum_time_ms': quantum_time_ms,
            'classical_time_ms': classical_time_ms,
            'time_speedup_factor': classical_time_ms / max(quantum_time_ms, 1),
            
            # Cost estimates
            'quantum_cost_usd': quantum_cost_usd,
            'classical_cost_usd': classical_cost_usd,
            'cost_difference_usd': abs(quantum_cost_usd - classical_cost_usd),
            
            # ROI Analysis
            'roi_quantum_vs_classical': roi_analysis['roi'],
            'cost_per_ms_quantum': quantum_cost_usd / max(quantum_time_ms, 1),
            'cost_per_ms_classical': classical_cost_usd / max(classical_time_ms, 1),
            
            # Budget validation
            'quantum_within_budget': budget_status['quantum_affordable'],
            'classical_within_budget': budget_status['classical_affordable'],
            'budget_limit_usd': budget_limit_usd,
            
            # Recommendation
            'cost_optimal_hardware': cost_optimal_hardware,
            'ml_suggestion': ml_hardware_suggestion.value,
            'cost_agrees_with_ml': (cost_optimal_hardware == ml_hardware_suggestion.value),
            
            # Metadata
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'confidence_level': self._calculate_cost_confidence(input_data)
        }
        
        logger.info(f"Cost Analysis: Q=${quantum_cost_usd:.4f} ({quantum_time_ms:.0f}ms) vs "
                   f"C=${classical_cost_usd:.4f} ({classical_time_ms:.0f}ms)")
        
        return analysis_result

    # ---------------------------------------------------------
    # QUANTUM EXECUTION TIME ESTIMATION
    # ---------------------------------------------------------
    
    def _estimate_quantum_time(self, input_data: CodeAnalysisInput) -> float:
        """
        Estimate quantum execution time in milliseconds
        Based on circuit characteristics and problem complexity
        """
        
        # Base time components
        base_circuit_time = input_data.circuit_depth * 0.1  # ~100ns per gate layer
        gate_execution_time = input_data.gate_count * 0.05  # ~50ns per gate
        shot_overhead = self.quantum_pricing['default_shots'] * 0.01  # Measurement time
        
        # Problem-specific overhead
        problem_overhead = self.problem_type_overhead.get(input_data.problem_type, 1.0)
        
        # Complexity adjustment
        complexity_multiplier = self.time_complexity_multipliers.get(
            input_data.time_complexity, 1.0
        )
        
        # NISQ hardware constraints (noise, calibration)
        nisq_overhead = 1.2  # 20% overhead for error mitigation
        
        # Total quantum time
        total_time_ms = (
            (base_circuit_time + gate_execution_time + shot_overhead) 
            * problem_overhead 
            * complexity_multiplier 
            * nisq_overhead
        )
        
        # Add queue time estimate (varies by provider load)
        queue_time_ms = self._estimate_queue_time(input_data.qubits_required)
        
        return max(total_time_ms + queue_time_ms, 10.0)  # Minimum 10ms

    # ---------------------------------------------------------
    # CLASSICAL EXECUTION TIME ESTIMATION
    # ---------------------------------------------------------
    
    def _estimate_classical_time(self, input_data: CodeAnalysisInput) -> float:
        """
        Estimate classical execution time in milliseconds
        Based on problem size and complexity
        """
        
        # Base computation time (problem size dependent)
        if input_data.time_complexity == TimeComplexity.EXPONENTIAL:
            # Exponential problems scale poorly on classical
            base_time = input_data.problem_size ** 2 * 0.1
        elif input_data.time_complexity == TimeComplexity.POLYNOMIAL:
            base_time = input_data.problem_size ** 1.5 * 0.05
        elif input_data.time_complexity == TimeComplexity.NLOGN:
            import math
            base_time = input_data.problem_size * math.log2(max(input_data.problem_size, 2)) * 0.01
        else:
            base_time = input_data.problem_size * 0.1
        
        # Memory access overhead
        memory_overhead = input_data.memory_requirement_mb * 0.01
        
        # Problem-specific adjustment
        problem_multiplier = {
            ProblemType.FACTORIZATION: 5.0,  # Very slow classically
            ProblemType.SEARCH: 2.0,         # Quadratic vs quantum linear
            ProblemType.SIMULATION: 3.0,     # Exponential state space
            ProblemType.OPTIMIZATION: 2.5,
            ProblemType.SORTING: 0.5,        # Fast classically
            ProblemType.DYNAMIC_PROGRAMMING: 1.0,
            ProblemType.MATRIX_OPS: 1.5,
            ProblemType.RANDOM_CIRCUIT: 1.0,
        }.get(input_data.problem_type, 1.0)
        
        total_time_ms = (base_time + memory_overhead) * problem_multiplier
        
        return max(total_time_ms, 1.0)  # Minimum 1ms

    # ---------------------------------------------------------
    # COST CALCULATION METHODS
    # ---------------------------------------------------------
    
    def _calculate_quantum_cost(self, input_data: CodeAnalysisInput, exec_time_ms: float) -> float:
        """Calculate quantum execution cost"""
        
        # Base task cost
        task_cost = self.quantum_pricing['base_cost_per_task']
        
        # Shot-based cost
        shot_cost = (self.quantum_pricing['default_shots'] * 
                    self.quantum_pricing['cost_per_shot'])
        
        # QPU time cost (convert ms to seconds)
        qpu_time_cost = (exec_time_ms / 1000.0) * self.quantum_pricing['cost_per_second']
        
        # Gate-based cost (operational overhead)
        gate_cost = input_data.gate_count * self.quantum_pricing['cost_per_gate']
        
        total_cost = task_cost + shot_cost + qpu_time_cost + gate_cost
        
        return round(total_cost, 6)
    
    def _calculate_classical_cost(self, input_data: CodeAnalysisInput, exec_time_ms: float) -> float:
        """Calculate classical execution cost"""
        
        # Compute time cost
        compute_cost = (exec_time_ms / 1000.0) * self.classical_pricing['cost_per_second']
        
        # Memory cost (GB-seconds)
        memory_gb = input_data.memory_requirement_mb / 1024.0
        memory_cost = memory_gb * (exec_time_ms / 1000.0) * self.classical_pricing['cost_per_gb_memory']
        
        # Base overhead
        overhead = self.classical_pricing['base_overhead']
        
        total_cost = compute_cost + memory_cost + overhead
        
        return round(total_cost, 6)

    # ---------------------------------------------------------
    # ROI AND DECISION SUPPORT
    # ---------------------------------------------------------
    
    def _calculate_roi(
        self, 
        quantum_cost: float, 
        classical_cost: float,
        quantum_time: float,
        classical_time: float
    ) -> Dict[str, float]:
        """
        Calculate Return on Investment for quantum vs classical
        
        ROI = (Time_Saved - Extra_Cost) / Extra_Cost
        """
        
        time_savings = classical_time - quantum_time
        cost_difference = quantum_cost - classical_cost
        
        if cost_difference <= 0:
            # Quantum is cheaper or same cost
            roi = float('inf') if time_savings > 0 else 0.0
        else:
            # Calculate ROI (higher is better)
            # Positive ROI means time savings justify extra cost
            roi = (time_savings / 1000.0 - cost_difference) / cost_difference
        
        return {
            'roi': round(roi, 2),
            'time_savings_ms': time_savings,
            'cost_difference_usd': cost_difference
        }
    
    def _check_budget_constraints(
        self, 
        quantum_cost: float,
        classical_cost: float,
        budget_limit: Optional[float]
    ) -> Dict[str, bool]:
        """Check if options fit within budget"""
        
        if budget_limit is None:
            return {
                'quantum_affordable': True,
                'classical_affordable': True,
                'budget_limit_set': False
            }
        
        return {
            'quantum_affordable': quantum_cost <= budget_limit,
            'classical_affordable': classical_cost <= budget_limit,
            'budget_limit_set': True
        }
    
    def _determine_cost_optimal_hardware(
        self,
        quantum_cost: float,
        classical_cost: float,
        quantum_time: float,
        classical_time: float,
        input_data: CodeAnalysisInput
    ) -> str:
        """
        Determine cost-optimal hardware considering both cost and time
        Uses a weighted decision model
        """
        
        # Cost factor (normalize to 0-1, classical=0, quantum=1)
        cost_diff = quantum_cost - classical_cost
        cost_factor = 1.0 / (1.0 + abs(cost_diff) * 10)  # Sigmoid-like
        
        # Time factor (normalize)
        time_speedup = classical_time / max(quantum_time, 1)
        time_factor = min(time_speedup / 10.0, 1.0)
        
        # Quantum advantage score (from input features)
        quantum_advantage = (
            input_data.superposition_score * 0.4 +
            input_data.entanglement_score * 0.4 +
            input_data.cx_gate_ratio * 0.2
        )
        
        # Weighted decision (prioritize cost, but consider speedup)
        cost_weight = 0.6
        time_weight = 0.3
        advantage_weight = 0.1
        
        quantum_score = (
            (1 - cost_factor) * cost_weight +  # Lower cost is better
            time_factor * time_weight +
            quantum_advantage * advantage_weight
        )
        
        # Decision threshold
        if quantum_score > 0.5:
            return HardwareType.QUANTUM.value
        else:
            return HardwareType.CLASSICAL.value
    
    def _estimate_queue_time(self, qubits_required: int) -> float:
        """
        Estimate queue waiting time based on qubit count
        Higher qubit systems typically have longer queues
        """
        if qubits_required <= 5:
            return 50.0  # ~50ms for small systems
        elif qubits_required <= 20:
            return 200.0  # ~200ms for medium systems
        else:
            return 500.0  # ~500ms for large systems
    
    def _calculate_cost_confidence(self, input_data: CodeAnalysisInput) -> float:
        """
        Calculate confidence in cost estimates
        Lower for edge cases (very large problems, many qubits)
        """
        confidence = 1.0
        
        # Reduce confidence for large qubit counts (NISQ uncertainty)
        if input_data.qubits_required > 30:
            confidence *= 0.8
        if input_data.qubits_required > 50:
            confidence *= 0.6
        
        # Reduce confidence for very deep circuits (noise accumulation)
        if input_data.circuit_depth > 500:
            confidence *= 0.9
        
        # Reduce confidence for very large problem sizes
        if input_data.problem_size > 1000:
            confidence *= 0.85
        
        return round(confidence, 2)