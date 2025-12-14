"""
Decision Merger Component
Intelligently combines ML predictions, rule-based decisions, and cost analysis
"""

import logging
from typing import Dict, Any, Optional

try:
    from ..schemas.decision_engine import (
        HardwareRecommendation,
        HardwareType
    )
    from .rule_service import RuleDecisionType
except ImportError:
    from schemas.decision_engine import (
        HardwareRecommendation,
        HardwareType
    )
    from services.rule_service import RuleDecisionType

logger = logging.getLogger(__name__)


class DecisionMerger:
    """
    Merges decisions from ML Model, Rule System, and Cost Analyzer
    Implements intelligent conflict resolution and confidence scoring
    """
    
    def __init__(self):
        """Initialize decision merger with weighting configuration"""
        
        # ---------------------------------------------------------
        # DECISION WEIGHT CONFIGURATION
        # ---------------------------------------------------------
        # These weights determine how much each component influences final decision
        
        self.decision_weights = {
            'ml_model': 0.50,        # ML predictions weight
            'rule_system': 0.35,     # Rule-based decisions weight
            'cost_analysis': 0.15,   # Cost optimization weight
        }
        
        # Confidence thresholds for decision validation
        self.confidence_thresholds = {
            'high_confidence': 0.85,
            'medium_confidence': 0.65,
            'low_confidence': 0.50,
        }

    def merge(
        self,
        ml_decision: Dict[str, Any],
        rule_decision: Dict[str, Any],
        cost_analysis: Dict[str, Any]
    ) -> HardwareRecommendation:
        """
        Merge all three decision sources into final recommendation
        
        Args:
            ml_decision: ML model prediction with confidence
            rule_decision: Rule-based system evaluation
            cost_analysis: Cost analyzer results
            
        Returns:
            HardwareRecommendation with final decision and rationale
        """
        
        logger.info("Merging decisions from ML, Rules, and Cost Analysis")
        
        # ---------------------------------------------------------
        # STEP 1: CHECK FOR OVERRIDING RULES
        # ---------------------------------------------------------
        # Rules can force decisions for safety/compatibility
        
        rule_override = self._check_rule_override(rule_decision)
        if rule_override is not None:
            logger.info(f"Rule override applied: {rule_override.rationale}")
            return rule_override
        
        # ---------------------------------------------------------
        # STEP 2: EXTRACT DECISIONS FROM EACH COMPONENT
        # ---------------------------------------------------------
        
        ml_hw = ml_decision['hardware']
        ml_confidence = ml_decision['confidence']
        ml_quantum_prob = ml_decision['quantum_probability']
        ml_classical_prob = ml_decision['classical_probability']
        
        rule_hw = rule_decision.get('hardware')  # May be None if ALLOW_BOTH
        rule_confidence = rule_decision.get('confidence', 0.5)
        
        cost_optimal_hw = HardwareType(cost_analysis['cost_optimal_hardware'])
        cost_agrees_with_ml = cost_analysis['cost_agrees_with_ml']
        
        # ---------------------------------------------------------
        # STEP 3: VOTING AND CONFIDENCE SCORING
        # ---------------------------------------------------------
        
        decision_scores = self._calculate_decision_scores(
            ml_hw, ml_confidence,
            rule_hw, rule_confidence,
            cost_optimal_hw,
            cost_agrees_with_ml
        )
        
        # ---------------------------------------------------------
        # STEP 4: FINAL DECISION SELECTION
        # ---------------------------------------------------------
        
        final_hardware = self._select_final_hardware(decision_scores)
        final_confidence = decision_scores[final_hardware.value]['total_score']
        
        # ---------------------------------------------------------
        # STEP 5: BUILD COMPREHENSIVE RATIONALE
        # ---------------------------------------------------------
        
        rationale = self._build_rationale(
            final_hardware,
            ml_decision,
            rule_decision,
            cost_analysis,
            decision_scores
        )
        
        # ---------------------------------------------------------
        # STEP 6: CONSTRUCT FINAL RECOMMENDATION
        # ---------------------------------------------------------
        
        recommendation = HardwareRecommendation(
            recommended_hardware=final_hardware,
            confidence=min(final_confidence, 1.0),
            quantum_probability=ml_quantum_prob,
            classical_probability=ml_classical_prob,
            rationale=rationale
        )
        
        logger.info(f"Final Decision: {final_hardware.value} (confidence: {final_confidence:.2%})")
        
        return recommendation

    # ---------------------------------------------------------
    # RULE OVERRIDE CHECKING
    # ---------------------------------------------------------
    
    def _check_rule_override(self, rule_decision: Dict[str, Any]) -> Optional[HardwareRecommendation]:
        """
        Check if rules force a specific decision (safety/compatibility)
        These override all other considerations
        """
        
        decision_type = rule_decision.get('decision_type')
        
        # FORCE_QUANTUM: Rules mandate quantum (e.g., only quantum compatible)
        if decision_type == RuleDecisionType.FORCE_QUANTUM:
            return HardwareRecommendation(
                recommended_hardware=HardwareType.QUANTUM,
                confidence=rule_decision.get('confidence', 1.0),
                quantum_probability=1.0,
                classical_probability=0.0,
                rationale=f"[RULE OVERRIDE] {rule_decision.get('rationale', 'Quantum required')}"
            )
        
        # FORCE_CLASSICAL: Rules mandate classical (e.g., safety constraint violated)
        if decision_type == RuleDecisionType.FORCE_CLASSICAL:
            return HardwareRecommendation(
                recommended_hardware=HardwareType.CLASSICAL,
                confidence=rule_decision.get('confidence', 1.0),
                quantum_probability=0.0,
                classical_probability=1.0,
                rationale=f"[RULE OVERRIDE] {rule_decision.get('rationale', 'Classical required')}"
            )
        
        # REJECT: Problem cannot be executed on any hardware
        if decision_type == RuleDecisionType.REJECT:
            return HardwareRecommendation(
                recommended_hardware=HardwareType.CLASSICAL,  # Default fallback
                confidence=0.0,
                quantum_probability=0.0,
                classical_probability=0.0,
                rationale=f"[REJECTED] {rule_decision.get('rationale', 'Problem exceeds all hardware limits')}"
            )
        
        # ALLOW_BOTH: No override, proceed with normal merging
        return None

    # ---------------------------------------------------------
    # DECISION SCORING
    # ---------------------------------------------------------
    
    def _calculate_decision_scores(
        self,
        ml_hw: HardwareType,
        ml_confidence: float,
        rule_hw: Optional[HardwareType],
        rule_confidence: float,
        cost_optimal_hw: HardwareType,
        cost_agrees_with_ml: bool
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate weighted scores for each hardware option
        """
        
        scores = {
            HardwareType.QUANTUM.value: {
                'ml_score': 0.0,
                'rule_score': 0.0,
                'cost_score': 0.0,
                'total_score': 0.0
            },
            HardwareType.CLASSICAL.value: {
                'ml_score': 0.0,
                'rule_score': 0.0,
                'cost_score': 0.0,
                'total_score': 0.0
            }
        }
        
        # ML Model Contribution
        ml_weight = self.decision_weights['ml_model']
        if ml_hw == HardwareType.QUANTUM:
            scores[HardwareType.QUANTUM.value]['ml_score'] = ml_confidence * ml_weight
            scores[HardwareType.CLASSICAL.value]['ml_score'] = (1 - ml_confidence) * ml_weight
        else:
            scores[HardwareType.CLASSICAL.value]['ml_score'] = ml_confidence * ml_weight
            scores[HardwareType.QUANTUM.value]['ml_score'] = (1 - ml_confidence) * ml_weight
        
        # Rule System Contribution
        rule_weight = self.decision_weights['rule_system']
        if rule_hw is not None:
            # Rule has a preference
            if rule_hw == HardwareType.QUANTUM:
                scores[HardwareType.QUANTUM.value]['rule_score'] = rule_confidence * rule_weight
                scores[HardwareType.CLASSICAL.value]['rule_score'] = (1 - rule_confidence) * rule_weight
            else:
                scores[HardwareType.CLASSICAL.value]['rule_score'] = rule_confidence * rule_weight
                scores[HardwareType.QUANTUM.value]['rule_score'] = (1 - rule_confidence) * rule_weight
        else:
            # Rule is neutral (ALLOW_BOTH), split weight evenly
            neutral_score = rule_weight * 0.5
            scores[HardwareType.QUANTUM.value]['rule_score'] = neutral_score
            scores[HardwareType.CLASSICAL.value]['rule_score'] = neutral_score
        
        # Cost Analysis Contribution
        cost_weight = self.decision_weights['cost_analysis']
        if cost_optimal_hw == HardwareType.QUANTUM:
            scores[HardwareType.QUANTUM.value]['cost_score'] = cost_weight
            scores[HardwareType.CLASSICAL.value]['cost_score'] = 0.0
        else:
            scores[HardwareType.CLASSICAL.value]['cost_score'] = cost_weight
            scores[HardwareType.QUANTUM.value]['cost_score'] = 0.0
        
        # Bonus if cost agrees with ML (increases confidence)
        agreement_bonus = 0.05
        if cost_agrees_with_ml:
            if ml_hw == HardwareType.QUANTUM:
                scores[HardwareType.QUANTUM.value]['cost_score'] += agreement_bonus
            else:
                scores[HardwareType.CLASSICAL.value]['cost_score'] += agreement_bonus
        
        # Calculate total scores
        for hw in [HardwareType.QUANTUM.value, HardwareType.CLASSICAL.value]:
            scores[hw]['total_score'] = (
                scores[hw]['ml_score'] +
                scores[hw]['rule_score'] +
                scores[hw]['cost_score']
            )
        
        return scores

    # ---------------------------------------------------------
    # FINAL HARDWARE SELECTION
    # ---------------------------------------------------------
    
    def _select_final_hardware(self, decision_scores: Dict[str, Dict[str, float]]) -> HardwareType:
        """
        Select final hardware based on total scores
        """
        
        quantum_score = decision_scores[HardwareType.QUANTUM.value]['total_score']
        classical_score = decision_scores[HardwareType.CLASSICAL.value]['total_score']
        
        logger.info(f"Decision Scores - Quantum: {quantum_score:.3f}, Classical: {classical_score:.3f}")
        
        # Select hardware with higher score
        if quantum_score > classical_score:
            return HardwareType.QUANTUM
        elif classical_score > quantum_score:
            return HardwareType.CLASSICAL
        else:
            # Tie - default to classical (safer, cheaper)
            logger.info("Score tie - defaulting to Classical")
            return HardwareType.CLASSICAL

    # ---------------------------------------------------------
    # RATIONALE BUILDING
    # ---------------------------------------------------------
    
    def _build_rationale(
        self,
        final_hardware: HardwareType,
        ml_decision: Dict[str, Any],
        rule_decision: Dict[str, Any],
        cost_analysis: Dict[str, Any],
        decision_scores: Dict[str, Dict[str, float]]
    ) -> str:
        """
        Build comprehensive human-readable rationale for the decision
        """
        
        rationale_parts = []
        
        # Primary decision statement
        confidence_level = self._get_confidence_level(
            decision_scores[final_hardware.value]['total_score']
        )
        rationale_parts.append(
            f"Recommendation: {final_hardware.value} with {confidence_level} confidence."
        )
        
        # ML Model contribution
        ml_hw = ml_decision['hardware']
        ml_conf = ml_decision['confidence']
        if ml_hw == final_hardware:
            rationale_parts.append(
                f"ML model supports this choice ({ml_conf:.1%} confidence)."
            )
        else:
            rationale_parts.append(
                f"ML model suggested {ml_hw.value} ({ml_conf:.1%}), but overridden by other factors."
            )
        
        # Rule System contribution
        rule_hw = rule_decision.get('hardware')
        if rule_hw is not None:
            if rule_hw == final_hardware:
                rationale_parts.append(
                    f"Rules support: {rule_decision.get('rationale', 'Compatible')}."
                )
            else:
                rationale_parts.append(
                    f"Rules suggested {rule_hw.value}: {rule_decision.get('rationale', '')}."
                )
        
        # Cost Analysis contribution
        cost_optimal = cost_analysis['cost_optimal_hardware']
        quantum_cost = cost_analysis['quantum_cost_usd']
        classical_cost = cost_analysis['classical_cost_usd']
        
        if final_hardware.value == cost_optimal:
            rationale_parts.append(
                f"Cost-optimal choice (${quantum_cost:.4f} vs ${classical_cost:.4f})."
            )
        else:
            rationale_parts.append(
                f"Cost analysis favors {cost_optimal}, but performance justifies ${abs(quantum_cost - classical_cost):.4f} premium."
            )
        
        # Performance estimates
        if final_hardware == HardwareType.QUANTUM:
            exec_time = cost_analysis['quantum_time_ms']
            speedup = cost_analysis['time_speedup_factor']
            rationale_parts.append(
                f"Estimated execution: {exec_time:.0f}ms ({speedup:.1f}x speedup over classical)."
            )
        else:
            exec_time = cost_analysis['classical_time_ms']
            rationale_parts.append(
                f"Estimated execution: {exec_time:.0f}ms on classical hardware."
            )
        
        return " ".join(rationale_parts)

    # ---------------------------------------------------------
    # HELPER METHODS
    # ---------------------------------------------------------
    
    def _get_confidence_level(self, score: float) -> str:
        """Convert numeric confidence score to human-readable level"""
        if score >= self.confidence_thresholds['high_confidence']:
            return "high"
        elif score >= self.confidence_thresholds['medium_confidence']:
            return "medium"
        else:
            return "low"