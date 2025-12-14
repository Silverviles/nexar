"""
Rule-Based System Component for Decision Engine
Implements threshold-based decision trees and hardware compatibility validation
"""

import logging
from typing import Dict, Optional, Any, List
from enum import Enum

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


class RuleDecisionType(str, Enum):
    """Types of rule-based decisions"""
    FORCE_QUANTUM = "force_quantum"
    FORCE_CLASSICAL = "force_classical"
    ALLOW_BOTH = "allow_both"
    REJECT = "reject"


class RuleBasedSystem:
    """
    Rule-based validation and decision system.
    Implements deterministic routing rules, safety constraints, and hardware compatibility.
    Research Objective SO2: Basic rule-based system with threshold rules.
    """
    
    def __init__(self):
        """Initialize rule-based system with decision thresholds"""
        
        # ---------------------------------------------------------
        # HARDWARE CAPABILITY CONSTRAINTS
        # ---------------------------------------------------------
        self.quantum_hardware_limits = {
            'max_qubits': 127,           # IBM Quantum Eagle limit
            'max_circuit_depth': 10000,  # Practical NISQ limit
            'max_gate_count': 100000,    # Operational limit
            'min_qubits': 2,             # Minimum for quantum advantage
        }
        
        self.classical_hardware_limits = {
            'max_memory_gb': 512,        # Typical cloud instance limit
            'max_problem_size': 1000000, # Large but feasible
        }
        
        # ---------------------------------------------------------
        # QUANTUM ADVANTAGE THRESHOLDS
        # ---------------------------------------------------------
        # These thresholds define when quantum hardware shows clear advantage
        
        self.quantum_advantage_thresholds = {
            'min_superposition_score': 0.6,
            'min_entanglement_score': 0.5,
            'min_cx_gate_ratio': 0.2,
            'min_combined_quantum_score': 0.65,  # Weighted average
        }
        
        # ---------------------------------------------------------
        # PROBLEM-SPECIFIC ROUTING RULES
        # ---------------------------------------------------------
        # Direct routing based on problem characteristics
        
        self.problem_type_rules = {
            ProblemType.FACTORIZATION: {
                'preferred_hardware': HardwareType.QUANTUM,
                'reason': "Shor's algorithm provides exponential speedup",
                'min_qubits': 8,
            },
            ProblemType.SEARCH: {
                'preferred_hardware': HardwareType.QUANTUM,
                'reason': "Grover's algorithm offers quadratic speedup",
                'min_qubits': 4,
            },
            ProblemType.SIMULATION: {
                'preferred_hardware': HardwareType.QUANTUM,
                'reason': "Quantum systems naturally simulate quantum phenomena",
                'min_qubits': 6,
            },
            ProblemType.OPTIMIZATION: {
                'preferred_hardware': HardwareType.QUANTUM,
                'reason': "QAOA/VQE can explore solution space efficiently",
                'min_qubits': 6,
            },
            ProblemType.SORTING: {
                'preferred_hardware': HardwareType.CLASSICAL,
                'reason': "Classical sorting algorithms are highly optimized",
                'quantum_not_beneficial': True,
            },
            ProblemType.DYNAMIC_PROGRAMMING: {
                'preferred_hardware': HardwareType.CLASSICAL,
                'reason': "Sequential dependencies limit quantum parallelism",
                'quantum_not_beneficial': True,
            },
            ProblemType.MATRIX_OPS: {
                'preferred_hardware': HardwareType.CLASSICAL,
                'reason': "Classical linear algebra libraries are mature and fast",
                'conditional': "quantum_if_very_large",  # Quantum might help for huge matrices
            },
        }
        
        # ---------------------------------------------------------
        # SAFETY CONSTRAINTS
        # ---------------------------------------------------------
        # Rules that must not be violated for system safety
        
        self.safety_rules = {
            'max_circuit_volume': 1000000,  # qubits * depth
            'max_noise_sensitivity': 50000,  # qubits * depth * cx_ratio
            'min_nisq_viability': 0.1,       # Minimum hardware viability score
        }

    def evaluate(self, input_data: CodeAnalysisInput) -> Dict[str, Any]:
        """
        Evaluate input against rule-based system
        
        Args:
            input_data: Code analysis input
            
        Returns:
            Rule-based decision with hardware recommendation and rationale
        """
        
        logger.info(f"Evaluating rules for {input_data.problem_type.value} problem")
        
        # ---------------------------------------------------------
        # STEP 1: HARDWARE COMPATIBILITY CHECK
        # ---------------------------------------------------------
        compatibility = self._check_hardware_compatibility(input_data)
        
        if not compatibility['quantum_compatible'] and not compatibility['classical_compatible']:
            return {
                'decision_type': RuleDecisionType.REJECT,
                'hardware': None,
                'confidence': 1.0,
                'rationale': "Problem exceeds both quantum and classical hardware limits",
                'compatibility': compatibility,
                'rules_triggered': ['hardware_limits_exceeded']
            }
        
        # ---------------------------------------------------------
        # STEP 2: SAFETY CONSTRAINT VALIDATION
        # ---------------------------------------------------------
        safety_check = self._validate_safety_constraints(input_data)
        
        if not safety_check['safe']:
            return {
                'decision_type': RuleDecisionType.FORCE_CLASSICAL,
                'hardware': HardwareType.CLASSICAL,
                'confidence': 1.0,
                'rationale': f"Safety constraint violated: {safety_check['violation_reason']}",
                'compatibility': compatibility,
                'rules_triggered': ['safety_constraint', safety_check['violated_rule']]
            }
        
        # ---------------------------------------------------------
        # STEP 3: CLEAR-CUT DECISION RULES
        # ---------------------------------------------------------
        clear_cut_decision = self._apply_clear_cut_rules(input_data, compatibility)
        
        if clear_cut_decision is not None:
            return clear_cut_decision
        
        # ---------------------------------------------------------
        # STEP 4: THRESHOLD-BASED QUANTUM ADVANTAGE ANALYSIS
        # ---------------------------------------------------------
        quantum_advantage = self._evaluate_quantum_advantage(input_data)
        
        if quantum_advantage['has_advantage'] and compatibility['quantum_compatible']:
            return {
                'decision_type': RuleDecisionType.FORCE_QUANTUM,
                'hardware': HardwareType.QUANTUM,
                'confidence': quantum_advantage['confidence'],
                'rationale': quantum_advantage['reason'],
                'compatibility': compatibility,
                'rules_triggered': ['quantum_advantage_threshold']
            }
        
        # ---------------------------------------------------------
        # STEP 5: PROBLEM-SPECIFIC ROUTING
        # ---------------------------------------------------------
        problem_based_decision = self._apply_problem_type_rules(input_data, compatibility)
        
        if problem_based_decision is not None:
            return problem_based_decision
        
        # ---------------------------------------------------------
        # STEP 6: DEFAULT - ALLOW ML MODEL TO DECIDE
        # ---------------------------------------------------------
        return {
            'decision_type': RuleDecisionType.ALLOW_BOTH,
            'hardware': None,  # Let ML model decide
            'confidence': 0.5,
            'rationale': "No clear rule applies; defer to ML model",
            'compatibility': compatibility,
            'rules_triggered': ['default_ml_decision']
        }

    # ---------------------------------------------------------
    # HARDWARE COMPATIBILITY CHECKING
    # ---------------------------------------------------------
    
    def _check_hardware_compatibility(self, input_data: CodeAnalysisInput) -> Dict[str, Any]:
        """
        Check if problem is compatible with quantum and/or classical hardware
        """
        
        quantum_issues = []
        classical_issues = []
        
        # Quantum compatibility checks
        if input_data.qubits_required < self.quantum_hardware_limits['min_qubits']:
            quantum_issues.append(f"Too few qubits ({input_data.qubits_required} < {self.quantum_hardware_limits['min_qubits']})")
        
        if input_data.qubits_required > self.quantum_hardware_limits['max_qubits']:
            quantum_issues.append(f"Exceeds qubit limit ({input_data.qubits_required} > {self.quantum_hardware_limits['max_qubits']})")
        
        if input_data.circuit_depth > self.quantum_hardware_limits['max_circuit_depth']:
            quantum_issues.append(f"Circuit too deep ({input_data.circuit_depth} > {self.quantum_hardware_limits['max_circuit_depth']})")
        
        if input_data.gate_count > self.quantum_hardware_limits['max_gate_count']:
            quantum_issues.append(f"Too many gates ({input_data.gate_count} > {self.quantum_hardware_limits['max_gate_count']})")
        
        # Classical compatibility checks
        memory_gb = input_data.memory_requirement_mb / 1024.0
        if memory_gb > self.classical_hardware_limits['max_memory_gb']:
            classical_issues.append(f"Exceeds memory limit ({memory_gb:.1f} GB > {self.classical_hardware_limits['max_memory_gb']} GB)")
        
        if input_data.problem_size > self.classical_hardware_limits['max_problem_size']:
            classical_issues.append(f"Problem size too large ({input_data.problem_size} > {self.classical_hardware_limits['max_problem_size']})")
        
        return {
            'quantum_compatible': len(quantum_issues) == 0,
            'classical_compatible': len(classical_issues) == 0,
            'quantum_issues': quantum_issues,
            'classical_issues': classical_issues,
        }

    # ---------------------------------------------------------
    # SAFETY CONSTRAINT VALIDATION
    # ---------------------------------------------------------
    
    def _validate_safety_constraints(self, input_data: CodeAnalysisInput) -> Dict[str, Any]:
        """
        Validate safety constraints to prevent dangerous operations
        """
        
        # Calculate circuit volume (indicator of decoherence risk)
        circuit_volume = input_data.qubits_required * input_data.circuit_depth
        
        if circuit_volume > self.safety_rules['max_circuit_volume']:
            return {
                'safe': False,
                'violation_reason': f"Circuit volume too high: {circuit_volume} > {self.safety_rules['max_circuit_volume']}",
                'violated_rule': 'max_circuit_volume'
            }
        
        # Calculate noise sensitivity
        noise_sensitivity = (input_data.qubits_required * 
                            input_data.circuit_depth * 
                            input_data.cx_gate_ratio)
        
        if noise_sensitivity > self.safety_rules['max_noise_sensitivity']:
            return {
                'safe': False,
                'violation_reason': f"Noise sensitivity too high: {noise_sensitivity:.0f} (risk of unreliable results)",
                'violated_rule': 'max_noise_sensitivity'
            }
        
        # Check NISQ viability (calculated from multiple factors)
        nisq_score = self._calculate_nisq_viability(input_data)
        
        if nisq_score < self.safety_rules['min_nisq_viability']:
            return {
                'safe': False,
                'violation_reason': f"NISQ viability too low: {nisq_score:.2f} (hardware cannot reliably execute)",
                'violated_rule': 'min_nisq_viability'
            }
        
        return {
            'safe': True,
            'violation_reason': None,
            'violated_rule': None
        }

    # ---------------------------------------------------------
    # CLEAR-CUT DECISION RULES
    # ---------------------------------------------------------
    
    def _apply_clear_cut_rules(
        self, 
        input_data: CodeAnalysisInput,
        compatibility: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Apply deterministic rules for obvious cases
        """
        
        # Rule 1: If only one hardware is compatible, use it
        if compatibility['quantum_compatible'] and not compatibility['classical_compatible']:
            return {
                'decision_type': RuleDecisionType.FORCE_QUANTUM,
                'hardware': HardwareType.QUANTUM,
                'confidence': 1.0,
                'rationale': "Only quantum hardware is compatible with requirements",
                'compatibility': compatibility,
                'rules_triggered': ['only_quantum_compatible']
            }
        
        if compatibility['classical_compatible'] and not compatibility['quantum_compatible']:
            return {
                'decision_type': RuleDecisionType.FORCE_CLASSICAL,
                'hardware': HardwareType.CLASSICAL,
                'confidence': 1.0,
                'rationale': f"Quantum incompatible: {', '.join(compatibility['quantum_issues'])}",
                'compatibility': compatibility,
                'rules_triggered': ['only_classical_compatible']
            }
        
        # Rule 2: Very small problems are not worth quantum overhead
        if input_data.problem_size < 10 and input_data.qubits_required < 5:
            return {
                'decision_type': RuleDecisionType.FORCE_CLASSICAL,
                'hardware': HardwareType.CLASSICAL,
                'confidence': 0.95,
                'rationale': "Problem too small to benefit from quantum overhead",
                'compatibility': compatibility,
                'rules_triggered': ['problem_too_small']
            }
        
        # Rule 3: No quantum characteristics → Classical
        if (input_data.qubits_required == 0 or 
            (input_data.superposition_score < 0.1 and input_data.entanglement_score < 0.1)):
            return {
                'decision_type': RuleDecisionType.FORCE_CLASSICAL,
                'hardware': HardwareType.CLASSICAL,
                'confidence': 0.98,
                'rationale': "No quantum characteristics detected in problem",
                'compatibility': compatibility,
                'rules_triggered': ['no_quantum_features']
            }
        
        return None  # No clear-cut rule applies

    # ---------------------------------------------------------
    # QUANTUM ADVANTAGE EVALUATION
    # ---------------------------------------------------------
    
    def _evaluate_quantum_advantage(self, input_data: CodeAnalysisInput) -> Dict[str, Any]:
        """
        Evaluate if problem exhibits clear quantum advantage based on thresholds
        """
        
        # Calculate weighted quantum score
        quantum_score = (
            input_data.superposition_score * 0.4 +
            input_data.entanglement_score * 0.4 +
            input_data.cx_gate_ratio * 0.2
        )
        
        reasons = []
        
        # Check individual thresholds
        if input_data.superposition_score >= self.quantum_advantage_thresholds['min_superposition_score']:
            reasons.append(f"High superposition potential ({input_data.superposition_score:.2f})")
        
        if input_data.entanglement_score >= self.quantum_advantage_thresholds['min_entanglement_score']:
            reasons.append(f"Strong entanglement ({input_data.entanglement_score:.2f})")
        
        if input_data.cx_gate_ratio >= self.quantum_advantage_thresholds['min_cx_gate_ratio']:
            reasons.append(f"High entangling gate usage ({input_data.cx_gate_ratio:.2f})")
        
        # Check time complexity for exponential problems
        if input_data.time_complexity == TimeComplexity.EXPONENTIAL:
            reasons.append("Exponential classical complexity")
        elif input_data.time_complexity == TimeComplexity.QUADRATIC_SPEEDUP:
            reasons.append("Known quantum speedup available")
        
        # Determine if advantage exists
        has_advantage = (
            quantum_score >= self.quantum_advantage_thresholds['min_combined_quantum_score'] or
            len(reasons) >= 3  # Multiple indicators suggest advantage
        )
        
        confidence = min(quantum_score * 1.2, 1.0)  # Scale confidence
        
        return {
            'has_advantage': has_advantage,
            'quantum_score': quantum_score,
            'confidence': confidence,
            'reason': "; ".join(reasons) if reasons else "No clear quantum advantage",
            'indicators': reasons
        }

    # ---------------------------------------------------------
    # PROBLEM-TYPE-SPECIFIC RULES
    # ---------------------------------------------------------
    
    def _apply_problem_type_rules(
        self,
        input_data: CodeAnalysisInput,
        compatibility: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Apply problem-type-specific routing rules
        """
        
        problem_rule = self.problem_type_rules.get(input_data.problem_type)
        
        if problem_rule is None:
            return None
        
        preferred_hw = problem_rule['preferred_hardware']
        reason = problem_rule['reason']
        
        # Check if preferred hardware is compatible
        if preferred_hw == HardwareType.QUANTUM:
            if not compatibility['quantum_compatible']:
                return None  # Can't use preferred hardware
            
            # Check minimum qubit requirement if specified
            min_qubits = problem_rule.get('min_qubits', 0)
            if input_data.qubits_required < min_qubits:
                return {
                    'decision_type': RuleDecisionType.FORCE_CLASSICAL,
                    'hardware': HardwareType.CLASSICAL,
                    'confidence': 0.85,
                    'rationale': f"Insufficient qubits ({input_data.qubits_required} < {min_qubits}) for quantum advantage in {input_data.problem_type.value}",
                    'compatibility': compatibility,
                    'rules_triggered': ['problem_type_min_qubits']
                }
            
            return {
                'decision_type': RuleDecisionType.FORCE_QUANTUM,
                'hardware': HardwareType.QUANTUM,
                'confidence': 0.85,
                'rationale': reason,
                'compatibility': compatibility,
                'rules_triggered': ['problem_type_quantum_preferred']
            }
        
        else:  # Classical preferred
            return {
                'decision_type': RuleDecisionType.FORCE_CLASSICAL,
                'hardware': HardwareType.CLASSICAL,
                'confidence': 0.90,
                'rationale': reason,
                'compatibility': compatibility,
                'rules_triggered': ['problem_type_classical_preferred']
            }

    # ---------------------------------------------------------
    # HELPER METHODS
    # ---------------------------------------------------------
    
    def _calculate_nisq_viability(self, input_data: CodeAnalysisInput) -> float:
        """
        Calculate NISQ era viability score
        Lower scores indicate hardware cannot reliably execute the circuit
        """
        viability = 1.0
        
        # Penalize excessive qubits
        if input_data.qubits_required > 50:
            viability *= 0.5
        if input_data.qubits_required > 80:
            viability *= 0.3
        
        # Penalize deep circuits (decoherence)
        if input_data.circuit_depth > 1000:
            viability *= 0.5
        if input_data.circuit_depth > 5000:
            viability *= 0.2
        
        # Penalize high circuit volume
        circuit_volume = input_data.qubits_required * input_data.circuit_depth
        if circuit_volume > 50000:
            viability *= 0.3
        
        return max(viability, 0.0)