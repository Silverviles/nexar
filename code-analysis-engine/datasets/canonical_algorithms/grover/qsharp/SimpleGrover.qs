namespace GroverSearch {
    open Microsoft.Quantum.Intrinsic;
    open Microsoft.Quantum.Measurement;
    open Microsoft.Quantum.Arrays;

    operation GroverSingleMarked() : Result[] {
        use qubits = Qubit[2];
        
        // Initial superposition
        H(qubits[0]);
        H(qubits[1]);
        
        // Oracle: mark |11⟩
        Z(qubits[0]);
        Z(qubits[1]);
        CZ(qubits[0], qubits[1]);
        
        // Diffusion operator
        H(qubits[0]);
        H(qubits[1]);
        X(qubits[0]);
        X(qubits[1]);
        CZ(qubits[0], qubits[1]);
        X(qubits[0]);
        X(qubits[1]);
        H(qubits[0]);
        H(qubits[1]);
        
        // Measure
        return ForEach(MResetZ, qubits);
    }
}
