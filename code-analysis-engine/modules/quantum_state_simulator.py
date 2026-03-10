"""
Quantum State Simulator for Accurate Superposition and Entanglement Scores
Uses state vector simulation to track actual quantum state evolution
"""
import logging
import numpy as np
from typing import List, Dict, Tuple, Optional
from models.unified_ast import UnifiedAST, QuantumGateNode, GateType
from scipy.stats import entropy

logger = logging.getLogger(__name__)

class QuantumStateSimulator:
    """
    Simulates quantum circuits to accurately measure:
    1. Superposition score (based on state entropy)
    2. Entanglement score (based on entanglement entropy)
    3. Actual quantum properties after gate application
    """
    
    def __init__(self, max_qubits: int = 20):
        """
        Initialize simulator
        
        Args:
            max_qubits: Maximum qubits to simulate (limited by memory: 2^n)
        """
        self.max_qubits = max_qubits
        self.state_vector = None
        self.num_qubits = 0
    
    def simulate(self, unified_ast: UnifiedAST) -> Dict[str, float]:
        """
        Simulate the quantum circuit and calculate scores
        
        Returns:
            {
                'superposition_score': float (0.0 to 1.0),
                'entanglement_score': float (0.0 to 1.0),
                'state_entropy': float,
                'max_entanglement_achieved': float
            }
        """
        self.num_qubits = unified_ast.total_qubits
        
        # Check if circuit is too large to simulate OR if qubits weren't detected
        if self.num_qubits == 0 or self.num_qubits > self.max_qubits:
            # Fall back to heuristic for large circuits or when qubits unknown
            logger.warning(
                "Circuit has %d qubits (max=%d), falling back to heuristic analysis",
                self.num_qubits, self.max_qubits,
            )
            return self._heuristic_analysis(unified_ast)
        
        # Initialize state to |00...0⟩
        self._initialize_state()
        
        # Track entropy throughout circuit
        entropy_history = [self._calculate_entropy()]
        entanglement_history = [0.0]
        
        # Apply gates sequentially (canonical IR first, AST fallback)
        gates = self._get_simulation_gates(unified_ast)
        for gate in gates:
            self._apply_gate(gate)
            entropy_history.append(self._calculate_entropy())
            entanglement_history.append(self._calculate_entanglement())
        
        # Calculate final scores
        superposition_score = max(
            self._normalize_entropy(e) for e in entropy_history
        )
        entanglement_score = max(entanglement_history)
        
        logger.debug(
            "Simulation complete: %d qubits, %d gates — superposition=%.3f, entanglement=%.3f",
            self.num_qubits, len(unified_ast.gates), superposition_score, entanglement_score,
        )
        
        return {
            'superposition_score': round(superposition_score, 3),
            'entanglement_score': round(entanglement_score, 3),
            'state_entropy': round(entropy_history[-1], 3),
            'max_entanglement_achieved': round(max(entanglement_history), 3),
            'final_state_purity': round(self._calculate_purity(), 3)
        }
    
    def _initialize_state(self):
        """Initialize quantum state to |00...0⟩"""
        dim = 2 ** self.num_qubits
        self.state_vector = np.zeros(dim, dtype=complex)
        self.state_vector[0] = 1.0  # |00...0⟩
    
    def _apply_gate(self, gate: QuantumGateNode):
        """Apply a quantum gate to the state vector"""
        gate_type = gate.gate_type
        
        # Get target qubits (convert to 0-indexed)
        targets = gate.qubits
        controls = gate.control_qubits
        
        if gate_type == GateType.H:
            self._apply_hadamard(targets[0] if targets else 0)
        
        elif gate_type == GateType.X:
            self._apply_pauli_x(targets[0] if targets else 0)
        
        elif gate_type == GateType.Y:
            self._apply_pauli_y(targets[0] if targets else 0)
        
        elif gate_type == GateType.Z:
            self._apply_pauli_z(targets[0] if targets else 0)
        
        elif gate_type == GateType.S:
            self._apply_s_gate(targets[0] if targets else 0)
        
        elif gate_type == GateType.T:
            self._apply_t_gate(targets[0] if targets else 0)
        
        elif gate_type in {GateType.RX, GateType.RY, GateType.RZ}:
            angle = gate.parameters[0] if gate.parameters else np.pi/4
            if gate_type == GateType.RX:
                self._apply_rx(targets[0] if targets else 0, angle)
            elif gate_type == GateType.RY:
                self._apply_ry(targets[0] if targets else 0, angle)
            else:  # RZ
                self._apply_rz(targets[0] if targets else 0, angle)
        
        elif gate_type in {GateType.CNOT, GateType.CX}:
            if controls and targets:
                self._apply_cnot(controls[0], targets[0])
        
        elif gate_type == GateType.CZ:
            if controls and targets:
                self._apply_cz(controls[0], targets[0])
        
        elif gate_type == GateType.SWAP:
            if len(targets) >= 2:
                self._apply_swap(targets[0], targets[1])
        
        elif gate_type == GateType.TOFFOLI:
            if len(controls) >= 2 and targets:
                self._apply_toffoli(controls[0], controls[1], targets[0])
        
        else:
            logger.debug("Unrecognized gate type %s, skipping", gate_type)
    
    # Single-qubit gate implementations
    
    def _apply_hadamard(self, qubit: int):
        """Apply Hadamard gate to qubit"""
        H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        self._apply_single_qubit_gate(qubit, H)
    
    def _apply_pauli_x(self, qubit: int):
        """Apply Pauli-X (NOT) gate"""
        X = np.array([[0, 1], [1, 0]])
        self._apply_single_qubit_gate(qubit, X)
    
    def _apply_pauli_y(self, qubit: int):
        """Apply Pauli-Y gate"""
        Y = np.array([[0, -1j], [1j, 0]])
        self._apply_single_qubit_gate(qubit, Y)
    
    def _apply_pauli_z(self, qubit: int):
        """Apply Pauli-Z gate"""
        Z = np.array([[1, 0], [0, -1]])
        self._apply_single_qubit_gate(qubit, Z)
    
    def _apply_s_gate(self, qubit: int):
        """Apply S gate (phase gate)"""
        S = np.array([[1, 0], [0, 1j]])
        self._apply_single_qubit_gate(qubit, S)
    
    def _apply_t_gate(self, qubit: int):
        """Apply T gate (π/8 gate)"""
        T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]])
        self._apply_single_qubit_gate(qubit, T)
    
    def _apply_rx(self, qubit: int, angle: float):
        """Apply RX rotation gate"""
        cos = np.cos(angle / 2)
        sin = np.sin(angle / 2)
        RX = np.array([[cos, -1j * sin], [-1j * sin, cos]])
        self._apply_single_qubit_gate(qubit, RX)
    
    def _apply_ry(self, qubit: int, angle: float):
        """Apply RY rotation gate"""
        cos = np.cos(angle / 2)
        sin = np.sin(angle / 2)
        RY = np.array([[cos, -sin], [sin, cos]])
        self._apply_single_qubit_gate(qubit, RY)
    
    def _apply_rz(self, qubit: int, angle: float):
        """Apply RZ rotation gate"""
        RZ = np.array([[np.exp(-1j * angle / 2), 0], 
                       [0, np.exp(1j * angle / 2)]])
        self._apply_single_qubit_gate(qubit, RZ)
    
    def _apply_single_qubit_gate(self, qubit: int, gate_matrix: np.ndarray):
        """
        Apply single-qubit gate using tensor product
        State update: |ψ⟩ → (I ⊗ ... ⊗ U ⊗ ... ⊗ I)|ψ⟩
        """
        # Handle edge cases
        if self.num_qubits == 0 or qubit < 0 or qubit >= self.num_qubits:
            return

        # Memory-efficient in-place pairwise update.
        # This is mathematically equivalent to applying the full tensor-product matrix,
        # but avoids allocating a 2^n x 2^n matrix.
        target_bit = 1 << (self.num_qubits - 1 - qubit)
        u00, u01 = gate_matrix[0, 0], gate_matrix[0, 1]
        u10, u11 = gate_matrix[1, 0], gate_matrix[1, 1]

        dim = len(self.state_vector)
        for i in range(dim):
            if i & target_bit:
                continue

            j = i | target_bit
            a0 = self.state_vector[i]
            a1 = self.state_vector[j]

            self.state_vector[i] = u00 * a0 + u01 * a1
            self.state_vector[j] = u10 * a0 + u11 * a1
    
    # Two-qubit gate implementations
    
    def _apply_cnot(self, control: int, target: int):
        """Apply CNOT (Controlled-X) gate"""
        dim = 2 ** self.num_qubits
        new_state = np.zeros_like(self.state_vector)

        for i in range(dim):
            amp = self.state_vector[i]
            if abs(amp) < 1e-12:
                continue

            if (i >> (self.num_qubits - 1 - control)) & 1:
                flipped = i ^ (1 << (self.num_qubits - 1 - target))
                new_state[flipped] += amp
            else:
                new_state[i] += amp

        self.state_vector = new_state
    
    def _apply_cz(self, control: int, target: int):
        """Apply CZ (Controlled-Z) gate"""
        dim = 2 ** self.num_qubits
        
        # CZ: if both control and target are 1, apply phase
        for i in range(dim):
            control_bit = (i >> (self.num_qubits - 1 - control)) & 1
            target_bit = (i >> (self.num_qubits - 1 - target)) & 1
            if control_bit and target_bit:
                self.state_vector[i] *= -1
    
    def _apply_swap(self, qubit1: int, qubit2: int):
        """Apply SWAP gate"""
        dim = 2 ** self.num_qubits
        new_state = np.copy(self.state_vector)
        
        for i in range(dim):
            # Extract bits
            bit1 = (i >> (self.num_qubits - 1 - qubit1)) & 1
            bit2 = (i >> (self.num_qubits - 1 - qubit2)) & 1
            
            if bit1 != bit2:
                # Swap bits
                swapped = i ^ (1 << (self.num_qubits - 1 - qubit1))
                swapped = swapped ^ (1 << (self.num_qubits - 1 - qubit2))
                new_state[swapped] = self.state_vector[i]
        
        self.state_vector = new_state
    
    def _apply_toffoli(self, control1: int, control2: int, target: int):
        """Apply Toffoli (CCX) gate"""
        dim = 2 ** self.num_qubits
        new_state = np.copy(self.state_vector)
        
        for i in range(dim):
            c1_bit = (i >> (self.num_qubits - 1 - control1)) & 1
            c2_bit = (i >> (self.num_qubits - 1 - control2)) & 1
            
            # If both controls are 1, flip target
            if c1_bit and c2_bit:
                flipped = i ^ (1 << (self.num_qubits - 1 - target))
                new_state[flipped] = self.state_vector[i]
                new_state[i] = self.state_vector[i]
        
        self.state_vector = new_state
    
    # Measurement and analysis methods
    
    def _calculate_entropy(self) -> float:
        """
        Calculate von Neumann entropy of the state
        S = -Σ pᵢ log₂(pᵢ)
        Measures superposition: 0 (pure) to n (max superposition)
        """
        probabilities = np.abs(self.state_vector) ** 2
        # Filter out zero probabilities
        probabilities = probabilities[probabilities > 1e-10]
        return entropy(probabilities, base=2)
    
    def _normalize_entropy(self, entropy_value: float) -> float:
        """
        Normalize entropy to [0, 1] range
        Max entropy = log₂(2^n) = n qubits
        """
        max_entropy = self.num_qubits
        if max_entropy == 0:
            return 0.0
        return min(entropy_value / max_entropy, 1.0)
    
    def _calculate_entanglement(self) -> float:
        """
        Calculate entanglement using Schmidt rank or mutual information
        
        For simplicity, we use a heuristic based on:
        - Purity of reduced density matrices
        - Number of non-zero Schmidt coefficients
        """
        if self.num_qubits < 2:
            return 0.0
        
        # Convert purity to entanglement score
        # Pure state (purity=1) → no entanglement (score=0)
        # Maximally mixed (purity=0.5 for single qubit) → max entanglement (score=1)
        ent_scores = []
        for q in range(self.num_qubits):
            purity = self._calculate_reduced_purity(q)
            score = (1.0 - purity) / 0.5
            ent_scores.append(score)

        return min(max(ent_scores), 1.0)
    
    def _calculate_reduced_purity(self, qubit: int) -> float:
        """
        Calculate purity of reduced density matrix for a qubit
        Tr(ρ²) where ρ is reduced density matrix
        """
        if self.num_qubits <= 1 or qubit < 0 or qubit >= self.num_qubits:
            return 1.0

        # Compute reduced 2x2 density matrix directly from state amplitudes.
        # Avoids constructing the full density matrix (which is O(4^n) memory).
        state_tensor = self.state_vector.reshape([2] * self.num_qubits)
        state_tensor = np.moveaxis(state_tensor, qubit, 0).reshape(2, -1)

        psi0 = state_tensor[0]
        psi1 = state_tensor[1]

        rho00 = float(np.vdot(psi0, psi0).real)
        rho11 = float(np.vdot(psi1, psi1).real)
        rho01 = np.sum(psi0 * np.conj(psi1))

        purity = rho00 * rho00 + rho11 * rho11 + 2.0 * (abs(rho01) ** 2)
        return float(max(0.0, min(1.0, purity.real)))
    
    def _calculate_purity(self) -> float:
        """Calculate purity of full state: Tr(|ψ⟩⟨ψ|²)"""
        # For pure states, purity = 1
        return np.real(np.sum(np.abs(self.state_vector) ** 4))
    
    def _heuristic_analysis(self, unified_ast: UnifiedAST) -> Dict[str, float]:
        """
        Fallback heuristic analysis for circuits too large to simulate
        Uses gate counting and patterns
        """
        gates = self._get_simulation_gates(unified_ast)
        total_gates = len(gates)
        
        # Superposition heuristic
        superposition_gates = {GateType.H, GateType.RX, GateType.RY}
        sup_count = sum(1 for g in gates if g.gate_type in superposition_gates)
        superposition_score = min(sup_count / max(unified_ast.total_qubits, 1), 1.0)
        
        # Entanglement heuristic
        entangling_gates = {GateType.CNOT, GateType.CX, GateType.CZ, 
                           GateType.SWAP, GateType.TOFFOLI}
        ent_count = sum(1 for g in gates if g.gate_type in entangling_gates)
        entanglement_score = min(ent_count / max(total_gates, 1), 1.0)
        
        # Boost if multiple qubits involved
        if unified_ast.total_qubits > 2:
            entanglement_score = min(entanglement_score * 1.5, 1.0)
        
        return {
            'superposition_score': round(superposition_score, 3),
            'entanglement_score': round(entanglement_score, 3),
            'state_entropy': 0.0,  # Can't calculate without simulation
            'max_entanglement_achieved': round(entanglement_score, 3),
            'final_state_purity': 0.0,
            'note': 'Heuristic analysis (circuit too large to simulate)'
        }

    def _get_simulation_gates(self, unified_ast: UnifiedAST) -> List[QuantumGateNode]:
        """Materialize simulator-friendly gate nodes from canonical IR when available."""
        if not unified_ast.canonical_ir or not unified_ast.canonical_ir.operations:
            logger.debug("Using AST gates directly (no canonical IR)")
            return unified_ast.gates if unified_ast.gates else []

        gates: List[QuantumGateNode] = []
        for op in unified_ast.canonical_ir.operations:
            if op.op_type != "gate" or not op.gate_name:
                continue
            gate_type = self._gate_type_from_ir_name(op.gate_name)
            if gate_type is None:
                logger.debug(f"Unknown gate type: {op.gate_name}")
                continue

            targets = list(op.target_qubits)
            controls = list(op.control_qubits)

            # SWAP uses 2 target qubits in the simulator path.
            if gate_type == GateType.SWAP and len(targets) < 2 and len(controls) >= 1:
                targets = [controls[0], targets[0]] if targets else controls[:2]
                controls = []

            gates.append(
                QuantumGateNode(
                    gate_type=gate_type,
                    qubits=targets,
                    parameters=list(op.parameters),
                    line_number=op.line_number,
                    is_controlled=bool(controls),
                    control_qubits=controls,
                )
            )
        
        logger.debug(f"Extracted {len(gates)} gates from canonical IR for simulation")
        return gates if gates else (unified_ast.gates if unified_ast.gates else [])

    def _gate_type_from_ir_name(self, gate_name: str) -> Optional[GateType]:
        for gate_type in GateType:
            if gate_type.value == gate_name:
                return gate_type
        return None


# Example usage
if __name__ == "__main__":
    from models.unified_ast import UnifiedAST, QuantumRegisterNode
    
    # Test case: Bell state (maximally entangled)
    bell_ast = UnifiedAST(
        source_language='qiskit',
        quantum_registers=[QuantumRegisterNode(name='q', size=2, line_number=1)],
        gates=[
            QuantumGateNode(gate_type=GateType.H, qubits=[0], line_number=2),
            QuantumGateNode(gate_type=GateType.CNOT, qubits=[1], 
                          control_qubits=[0], is_controlled=True, line_number=3)
        ],
        total_qubits=2,
        total_gates=2
    )
    
    simulator = QuantumStateSimulator()
    result = simulator.simulate(bell_ast)
    
    logger.info("Bell State Analysis:")
    logger.info("Superposition Score: %s", result['superposition_score'])
    logger.info("Entanglement Score: %s", result['entanglement_score'])
    logger.info("State Entropy: %s", result['state_entropy'])
    logger.info("Expected: High superposition and entanglement (~1.0)")

    print("Bell State Analysis:")
    print(f"Superposition Score: {result['superposition_score']}")
    print(f"Entanglement Score: {result['entanglement_score']}")
    print(f"State Entropy: {result['state_entropy']}")
    print(f"Expected: High superposition and entanglement (~1.0)")