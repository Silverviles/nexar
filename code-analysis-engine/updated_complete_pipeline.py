"""
Updated Complete Pipeline
Canonical Collection → Validation → Smart Variation → Multi-Label Training

This pipeline solves the 3 problems:
1. Uses canonical implementations from trusted sources
2. Multi-label classification (detects multiple algorithms)
3. Smart variations with diverse features
"""
import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, List

sys.path.append(str(Path(__file__).parent.parent))

from datasets.canonical_algorithm_collector import (
    CanonicalAlgorithmCollector,
    ManualAlgorithmAdder
)
from datasets.algorithm_validators import AlgorithmValidatorFactory
from datasets.smart_variation_generator import SmartVariationGenerator
import subprocess

class ImprovedQuantumMLPipeline:
    """
    Improved ML pipeline addressing all 3 problems:
    
    1. ✅ Canonical implementations from trusted sources
    2. ✅ Multi-label classification 
    3. ✅ Smart variations with diverse features
    """
    
    def __init__(self):
        self.canonical_collector = CanonicalAlgorithmCollector()
        self.variation_generator = SmartVariationGenerator()
        self.validator_factory = AlgorithmValidatorFactory()
        
        self.canonical_dir = Path("datasets/canonical_algorithms")
        self.variations_dir = Path("datasets/algorithm_variations")
        self.variations_dir.mkdir(parents=True, exist_ok=True)
    
    def step1_collect_canonical(self):
        """
        STEP 1: Collect canonical implementations from trusted sources
        """
        print("\n" + "="*80)
        print("STEP 1: COLLECTING CANONICAL IMPLEMENTATIONS")
        print("="*80)
        
        print("\n📚 Collecting from trusted sources...")
        print("   - Qiskit Textbook")
        print("   - Microsoft Q# Samples")
        print("   - Google Cirq Tutorials")
        print("   - OpenQASM Examples")
        print()
        
        # Automated collection (limited by API access)
        self.canonical_collector.collect_microsoft_qsharp_samples()
        
        # Manual addition instructions
        print("\n" + "="*80)
        print("MANUAL ADDITION REQUIRED")
        print("="*80)
        print("\nMany canonical sources require manual extraction:")
        print()
        print("1. Qiskit Textbook (Jupyter notebooks):")
        print("   - Download: https://github.com/Qiskit/textbook")
        print("   - Extract code cells using nbconvert")
        print("   - Add using ManualAlgorithmAdder")
        print()
        print("2. Cirq Tutorials:")
        print("   - Visit: https://quantumai.google/cirq/tutorials")
        print("   - Copy canonical examples")
        print("   - Add manually")
        print()
        print("3. Validation:")
        print("   - Each added algorithm is automatically validated")
        print("   - Only textbook-correct implementations accepted")
        print()
        
        # Example manual addition
        adder = ManualAlgorithmAdder(self.canonical_collector)
        
        adder.add_from_file(
            "datasets/canonical_algorithms/bernstein_vazirani/cirq/bernstein_vazirani.py",
            algorithm="bernstein_vazirani",
            language="cirq",
            source_url="https://github.com/quantumlib/Cirq/blob/main/examples/bernstein_vazirani.py"
        )
        adder.add_from_file(
            "datasets/canonical_algorithms/bernstein_vazirani/openqasm/bv_n14.qasm",
            algorithm="bernstein_vazirani",
            language="openqasm",
            source_url="https://github.com/uuudown/QASMBench/blob/master/medium/bv_n14/bv_n14.qasm"
        )
        adder.add_from_file(
            "datasets/canonical_algorithms/bernstein_vazirani/qiskit/bernstein-vazirani.py",
            algorithm="bernstein_vazirani",
            language="qiskit",
            source_url="https://github.com/Qiskit/textbook/blob/main/notebooks/ch-algorithms/bernstein-vazirani.ipynb"
        )
        adder.add_from_file(
            "datasets/canonical_algorithms/bernstein_vazirani/qsharp/BernsteinVazirani.qs",
            algorithm="bernstein_vazirani",
            language="qsharp",
            source_url="https://github.com/microsoft/Quantum/blob/main/samples/getting-started/simple-algorithms/BernsteinVazirani.qs"
        )
        adder.add_from_file(
            "datasets/canonical_algorithms/deutsch_jozsa/qiskit/deutsch-jozsa.py",
            algorithm="deutsch_jozsa",
            language="qiskit",
            source_url="https://github.com/Qiskit/textbook/blob/main/notebooks/ch-algorithms/deutsch-jozsa.ipynb"
        )
        adder.add_from_file(
            "datasets/canonical_algorithms/deutsch_jozsa/qsharp/DeutschJozsa.qs",
            algorithm="deutsch_jozsa",
            language="qsharp",
            source_url="https://github.com/microsoft/Quantum/blob/main/samples/getting-started/simple-algorithms/DeutschJozsa.qs"
        )
        adder.add_from_file(
            "datasets/canonical_algorithms/deutsch_jozsa/qsharp/DeutschJozsa.qs",
            algorithm="deutsch_jozsa",
            language="qsharp",
            source_url="https://github.com/microsoft/Quantum/blob/main/samples/getting-started/simple-algorithms/DeutschJozsa.qs"
        )
        adder.add_from_file(
            "datasets/canonical_algorithms/grover/cirq/grover.py",
            algorithm="grover",
            language="cirq",
            source_url="https://github.com/quantumlib/Cirq/blob/main/examples/grover.py"
        )
        adder.add_from_file(
            "datasets/canonical_algorithms/grover/qiskit/grover.py",
            algorithm="grover",
            language="qiskit",
            source_url="https://github.com/Qiskit/textbook/blob/main/notebooks/ch-algorithms/grover.ipynb"
        )
        adder.add_from_file(
            "datasets/canonical_algorithms/grover/qsharp/SimpleGrover.qs",
            algorithm="grover",
            language="qsharp",
            source_url="https://github.com/microsoft/Quantum/blob/main/samples/algorithms/simple-grover/SimpleGrover.qs"
        )
        adder.add_from_file(
            "datasets/canonical_algorithms/qaoa/openqasm/qaoa_n6.qasm",
            algorithm="qaoa",
            language="openqasm",
            source_url="https://github.com/uuudown/QASMBench/blob/master/medium/qaoa_n6/qaoa_n6.qasm"
        )
        adder.add_from_file(
            "datasets/canonical_algorithms/qft/openqasm/qft_n15.qasm",
            algorithm="qft",
            language="openqasm",
            source_url="https://github.com/uuudown/QASMBench/blob/master/medium/qft_n15/qft_n15.qasm"
        )
        adder.add_from_file(
            "datasets/canonical_algorithms/qft/qiskit/quantum-fourier-transform.py",
            algorithm="qft",
            language="qiskit",
            source_url="https://github.com/Qiskit/textbook/blob/main/notebooks/ch-algorithms/quantum-fourier-transform.ipynb"
        )
        adder.add_from_file(
            "datasets/canonical_algorithms/qpe/qiskit/quantum-phase-estimation.py",
            algorithm="qpe",
            language="qiskit",
            source_url="https://github.com/Qiskit/textbook/blob/main/notebooks/ch-algorithms/quantum-phase-estimation.ipynb"
        )
        adder.add_from_file(
            "datasets/canonical_algorithms/shor/qiskit/shor.py",
            algorithm="shor",
            language="qiskit",
            source_url="https://github.com/Qiskit/textbook/blob/main/notebooks/ch-algorithms/shor.ipynb"
        )
        adder.add_from_file(
            "datasets/canonical_algorithms/simon/openqasm/simon_n6.qasm",
            algorithm="simon",
            language="openqasm",
            source_url="https://github.com/uuudown/QASMBench/blob/master/medium/simon_n6/simon_n6.qasm"
        )
        adder.add_from_file(
            "datasets/canonical_algorithms/simon/qiskit/simon.py",
            algorithm="simon",
            language="qiskit",
            source_url="https://github.com/Qiskit/textbook/blob/main/notebooks/ch-algorithms/simon.ipynb"
        )

        print("Example usage:")
        print("  adder.add_from_file(")
        print("      'path/to/grover_canonical.py',")
        print("      algorithm='grover',")
        print("      language='qiskit',")
        print("      source_url='https://qiskit.org/textbook/ch-algorithms/grover.html'")
        print("  )")
        print()
        
        # Save what we have
        if self.canonical_collector.implementations:
            self.canonical_collector.save_canonical_dataset()
            self.canonical_collector.generate_collection_report()
        
        return len(self.canonical_collector.implementations)
    
    def step2_validate_canonical(self):
        """
        STEP 2: Validate all collected implementations
        """
        print("\n" + "="*80)
        print("STEP 2: VALIDATING CANONICAL IMPLEMENTATIONS")
        print("="*80)
        
        if not self.canonical_collector.implementations:
            print("\n⚠️  No canonical implementations to validate")
            print("   Please complete Step 1 first")
            return
        
        print(f"\n📊 Validating {len(self.canonical_collector.implementations)} implementations...")
        
        validation_results = {}
        
        for impl in self.canonical_collector.implementations:
            validator = self.validator_factory.get_validator(impl.algorithm)
            
            if not validator:
                print(f"  ⚠️  No validator for {impl.algorithm}")
                continue
            
            result = validator.validate(impl.code)
            validation_results[impl.hash] = result
            
            status = "✅" if result.is_valid else "❌"
            print(f"  {status} {impl.algorithm} ({impl.language}): "
                  f"{result.confidence:.0%} confidence")
            
            # Update implementation
            impl.verified = result.is_valid
        
        # Save validation report
        report_file = self.canonical_dir / 'validation_report.json'
        with open(report_file, 'w') as f:
            json.dump({
                'total': len(validation_results),
                'valid': sum(1 for r in validation_results.values() if r.is_valid),
                'results': {
                    h: {
                        'is_valid': r.is_valid,
                        'confidence': r.confidence,
                        'violations': r.violations,
                        'requirements_met': r.requirements_met
                    }
                    for h, r in validation_results.items()
                }
            }, f, indent=2)
        
        valid_count = sum(1 for impl in self.canonical_collector.implementations 
                         if impl.verified)
        
        print(f"\n✅ Validation complete!")
        print(f"   Valid: {valid_count}/{len(self.canonical_collector.implementations)}")
        print(f"   Report saved: {report_file}")
        
        return valid_count
    
    def step3_generate_smart_variations(self, variations_per_canonical: int = 50):
        """
        STEP 3: Generate smart variations with diverse features
        """
        print("\n" + "="*80)
        print("STEP 3: GENERATING SMART VARIATIONS")
        print("="*80)
        
        if not self.canonical_collector.implementations:
            print("\n⚠️  No canonical implementations")
            return 0
        
        # Only use verified implementations
        verified_impls = [
            impl for impl in self.canonical_collector.implementations
            if impl.verified
        ]
        
        if not verified_impls:
            print("\n⚠️  No verified canonical implementations")
            print("   Please complete Step 2 validation")
            return 0
        
        print(f"\n🔄 Generating {variations_per_canonical} variations per canonical...")
        print(f"   Canonical implementations: {len(verified_impls)}")
        print(f"   Target variations: {len(verified_impls) * variations_per_canonical}")
        print()
        
        total_variations = 0
        
        for impl in verified_impls:
            print(f"\n📊 {impl.algorithm} ({impl.language})...")
            
            # Parse to AST
            from modules.language_detector import LanguageDetector, SupportedLanguage
            from modules.ast_builder import ASTBuilder
            
            try:
                lang_detector = LanguageDetector()
                ast_builder = ASTBuilder()
                
                detected_lang = SupportedLanguage(impl.language)
                base_ast = ast_builder.build(impl.code, detected_lang)

                # Strict quality gate: skip canonicals with unresolved parser output.
                if not self._is_ast_quality_ok(base_ast):
                    print("  ⚠️  Skipping canonical due to low parser quality (empty qubits/gates)")
                    continue
                
                # Generate variations
                variations = self.variation_generator.generate_variations(
                    base_ast,
                    impl.algorithm,
                    count=variations_per_canonical,
                    diversity_level='high'
                )
                
                total_variations += len(variations)
                
                # Save variations
                self._save_variations(impl, variations)
                
            except Exception as e:
                print(f"  ❌ Error generating variations: {e}")
                continue
        
        print(f"\n✅ Generated {total_variations} total variations!")
        print(f"   Location: {self.variations_dir}")
        
        return total_variations
    
    def _save_variations(self, canonical_impl, variations):
        """Save generated variations"""
        algo_dir = self.variations_dir / canonical_impl.algorithm / canonical_impl.language
        algo_dir.mkdir(parents=True, exist_ok=True)

        saved_count = 0
        skipped_count = 0
        
        for i, (varied_ast, metadata) in enumerate(variations):
            if not self._is_ast_quality_ok(varied_ast):
                skipped_count += 1
                continue

            # Generate code representation from AST for CodeBERT training
            code_representation = self._ast_to_code(varied_ast, canonical_impl.language)

            if not code_representation.strip():
                skipped_count += 1
                continue
            
            # Serialize AST to JSON with code field
            variation_data = {
                'canonical_hash': canonical_impl.hash,
                'variation_id': i,
                'algorithm': canonical_impl.algorithm,
                'language': canonical_impl.language,
                'metadata': metadata,
                'code': code_representation,  # Add code field for CodeBERT
                'ir': varied_ast.to_ir()
            }
            
            variation_file = algo_dir / f"variation_{canonical_impl.hash[:8]}_{i:04d}.json"
            with open(variation_file, 'w') as f:
                json.dump(variation_data, f, indent=2)

            saved_count += 1

        if skipped_count > 0:
            print(f"   ⚠️  Skipped {skipped_count} low-quality variations, saved {saved_count}")

    def _is_ast_quality_ok(self, ast) -> bool:
        """Reject ASTs that indicate unresolved parser output."""
        if ast is None:
            return False
        if ast.total_qubits is None or ast.total_qubits <= 0:
            return False
        if not ast.gates:
            return False

        gate_ops = [g for g in ast.gates if g.gate_type.name.lower() != 'barrier']
        if not gate_ops:
            return False

        empty_gate_count = sum(
            1 for g in gate_ops if not g.qubits and not (g.control_qubits or [])
        )
        return empty_gate_count == 0
    
    def _ast_to_code(self, ast, language: str) -> str:
        """
        Convert UnifiedAST to code representation for CodeBERT training
        
        Generates a simple but valid code representation that preserves
        the semantic structure for CodeBERT to learn from.
        """
        from models.unified_ast import GateType
        
        lines = []
        
        # Header based on language
        if language == 'qiskit':
            lines.append("from qiskit import QuantumCircuit")
            lines.append(f"qc = QuantumCircuit({ast.total_qubits})")
        elif language == 'cirq':
            lines.append("import cirq")
            lines.append(f"qubits = [cirq.LineQubit(i) for i in range({ast.total_qubits})]")
            lines.append("circuit = cirq.Circuit()")
        elif language == 'qsharp':
            lines.append("operation QuantumAlgorithm() : Unit {")
            lines.append(f"    use qubits = Qubit[{ast.total_qubits}];")
        elif language == 'openqasm':
            lines.append("OPENQASM 2.0;")
            lines.append('include "qelib1.inc";')
            lines.append(f"qreg q[{ast.total_qubits}];")
        
        # Generate gate operations
        for gate in ast.gates:
            gate_line = self._gate_to_code(gate, language)
            if gate_line:
                lines.append(gate_line)
        
        # Footer
        if language == 'qsharp':
            lines.append("}")
        
        return '\n'.join(lines)
    
    def _gate_to_code(self, gate, language: str) -> str:
        """Convert a single gate to code representation"""
        from models.unified_ast import GateType
        
        gate_name = gate.gate_type.name.lower()
        qubits = gate.qubits
        
        if language == 'qiskit':
            if gate.is_controlled and gate.control_qubits:
                targets = ', '.join(map(str, qubits))
                controls = ', '.join(map(str, gate.control_qubits))
                if gate.gate_type == GateType.CX or gate.gate_type == GateType.CNOT:
                    return f"qc.cx({controls}, {targets})"
                elif gate.gate_type == GateType.CZ:
                    return f"qc.cz({controls}, {targets})"
                else:
                    return f"qc.c{gate_name}({controls}, {targets})"
            else:
                qubit_str = ', '.join(map(str, qubits))
                if gate.parameters:
                    params = ', '.join([f"{p:.4f}" for p in gate.parameters])
                    return f"qc.{gate_name}({params}, {qubit_str})"
                else:
                    return f"qc.{gate_name}({qubit_str})"
        
        elif language == 'cirq':
            qubit_str = ', '.join([f"qubits[{q}]" for q in qubits])
            if gate.is_controlled and gate.control_qubits:
                control_str = ', '.join([f"qubits[{q}]" for q in gate.control_qubits])
                return f"circuit.append(cirq.{gate_name.upper()}({qubit_str}).controlled_by({control_str}))"
            else:
                return f"circuit.append(cirq.{gate_name.upper()}({qubit_str}))"
        
        elif language == 'openqasm':
            qubit_str = ', '.join([f"q[{q}]" for q in qubits])
            if gate.is_controlled and gate.control_qubits:
                control_str = ', '.join([f"q[{q}]" for q in gate.control_qubits])
                return f"c{gate_name} {control_str}, {qubit_str};"
            else:
                return f"{gate_name} {qubit_str};"
        
        elif language == 'qsharp':
            qubit_str = ', '.join([f"qubits[{q}]" for q in qubits])
            if gate.is_controlled and gate.control_qubits:
                control_str = ', '.join([f"qubits[{q}]" for q in gate.control_qubits])
                return f"    Controlled {gate_name.upper()}([{control_str}], ({qubit_str}));"
            else:
                return f"    {gate_name.upper()}({qubit_str});"
        
        return ""
    
    def step4_train_multilabel_classifier(self):
        """
        STEP 4: DEPRECATED - Use Step 5 (CodeBERT) instead
        
        The old feature-based multi-label classifier has been deprecated.
        Use Step 5 to train CodeBERT for 85-95% accuracy.
        """
        print("\n" + "="*80)
        print("STEP 4: DEPRECATED")
        print("="*80)
        
        print("\n⚠️  Step 4 (feature-based multi-label classifier) is DEPRECATED")
        print("   Reason: Poor accuracy (0-20%) with grouped train/test split")
        print()
        print("✅ Use Step 5 instead:")
        print("   python updated_complete_pipeline.py --step 5 --epochs 10")
        print()
        print("📊 Expected results:")
        print("   Step 4 (old): 0-20% accuracy")
        print("   Step 5 (CodeBERT): 85-95% accuracy")
        print()
        print("💡 CodeBERT uses semantic understanding instead of surface features")
        print("="*80)
        
        return None
    
    def step5_train_codebert_classifier(
        self,
        epochs: int = 10,
        batch_size: int = 16,
        learning_rate: float = 2e-5
    ):
        """
        STEP 5: Train CodeBERT algorithm classifier - HIGH ACCURACY MODEL
        
        This uses transformer-based semantic understanding instead of feature extraction.
        Expected accuracy: 85-100% (much better than feature-based ML)
        """
        print("\n" + "="*80)
        print("STEP 5: TRAINING CODEBERT ALGORITHM CLASSIFIER (RECOMMENDED)")
        print("="*80)
        
        print("\n🚀 CodeBERT uses transformer-based semantic understanding")
        print("   ✅ Understands code semantically (not just surface features)")
        print("   ✅ Generalizes across languages (Qiskit, Cirq, Q#, OpenQASM)")
        print("   ✅ Multi-label detection (multiple algorithms per code)")
        print("   ✅ Expected accuracy: 85-100%")
        print()
        
        # Check if we have variations
        if not self.variations_dir.exists():
            print("⚠️  No variations found. Run Step 3 first.")
            return None
        
        variation_files = list(self.variations_dir.rglob('variation_*.json'))
        if len(variation_files) == 0:
            print("⚠️  No variation files found. Run Step 3 first.")
            return None
        
        print(f"✅ Found {len(variation_files)} variation files")
        print()
        
        # Build command
        cmd = [
            sys.executable,
            "train_codebert_algorithm_classifier.py",
            "--variations-path", str(self.variations_dir),
            "--epochs", str(epochs),
            "--batch-size", str(batch_size),
            "--learning-rate", str(learning_rate),
            "--test-size", "0.2",
            "--threshold", "0.5"
        ]
        
        print("🏃 Starting CodeBERT training...")
        print(f"   Command: {' '.join(cmd)}")
        print()
        
        try:
            # Run training script
            result = subprocess.run(cmd, check=True)
            
            print("\n✅ CodeBERT training completed successfully!")
            print("   Model saved to: models/trained_codebert/")
            print()
            print("💡 To use the model:")
            print("   1. Restart your FastAPI server (main.py)")
            print("   2. CodeBERT will be auto-loaded on startup")
            print("   3. API will use CodeBERT for high-accuracy algorithm detection")
            print()
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"\n❌ CodeBERT training failed with error: {e}")
            print("   Check the error output above")
            return None
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_summary_report(self):
        """Generate comprehensive pipeline report"""
        print("\n" + "="*80)
        print("PIPELINE SUMMARY REPORT")
        print("="*80)
        
        # Canonical stats
        canonical_count = len(self.canonical_collector.implementations)
        verified_count = sum(1 for impl in self.canonical_collector.implementations 
                            if impl.verified)
        
        print(f"\n📚 CANONICAL IMPLEMENTATIONS:")
        print(f"   Total collected: {canonical_count}")
        print(f"   Verified: {verified_count}")
        
        if canonical_count > 0:
            print(f"\n   By Algorithm:")
            algo_counts = {}
            for impl in self.canonical_collector.implementations:
                algo_counts[impl.algorithm] = algo_counts.get(impl.algorithm, 0) + 1
            
            for algo, count in sorted(algo_counts.items()):
                verified = sum(1 for impl in self.canonical_collector.implementations
                             if impl.algorithm == algo and impl.verified)
                print(f"      {algo}: {count} ({verified} verified)")
        
        # Variation stats
        if self.variations_dir.exists():
            variation_files = list(self.variations_dir.rglob('variation_*.json'))
            print(f"\n🔄 VARIATIONS:")
            print(f"   Total generated: {len(variation_files)}")
        
        # Recommendations
        print(f"\n💡 NEXT STEPS:")
        
        if canonical_count == 0:
            print("   1. ❌ Collect canonical implementations (Step 1)")
            print("      → Add from Qiskit Textbook, Q# samples, etc.")
        elif verified_count == 0:
            print("   1. ✅ Canonical implementations collected")
            print("   2. ❌ Validate implementations (Step 2)")
        elif not self.variations_dir.exists() or len(list(self.variations_dir.rglob('*.json'))) == 0:
            print("   1. ✅ Canonical implementations collected & validated")
            print("   2. ❌ Generate smart variations (Step 3)")
        else:
            print("   1. ✅ Canonical implementations ready")
            print("   2. ✅ Smart variations generated")
            print("   3. ❌ Train CodeBERT classifier (Step 5)")
            print("      → python updated_complete_pipeline.py --step 5")
        
        print("\n" + "="*80)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main(variations_per_canonical=50):
    print("╔" + "="*78 + "╗")
    print("║" + " "*15 + "IMPROVED QUANTUM ALGORITHM ML PIPELINE" + " "*24 + "║")
    print("╚" + "="*78 + "╝")
    print()
    print("This pipeline solves 3 critical problems:")
    print("  1. ✅ Uses CANONICAL implementations from trusted sources")
    print("  2. ✅ MULTI-LABEL classification (detects multiple algorithms)")
    print("  3. ✅ SMART VARIATIONS with diverse features")
    print()
    
    pipeline = ImprovedQuantumMLPipeline()
    
    # Run pipeline steps
    print("="*80)
    print("PIPELINE EXECUTION")
    print("="*80)
    
    start_time = time.time()
    
    # Step 1: Collect canonical
    canonical_count = pipeline.step1_collect_canonical()
    
    # Step 2: Validate (if we have implementations)
    if canonical_count > 0:
        verified_count = pipeline.step2_validate_canonical()
        
        # Step 3: Generate variations (if we have verified implementations)
        if verified_count > 0:
            # Use default or command line arg for variations
            variation_count = pipeline.step3_generate_smart_variations(
                variations_per_canonical=variations_per_canonical
            )
            
            # Step 5: Train CodeBERT classifier (recommended)
            print("\n💡 To train the algorithm classifier, run:")
            print("   python updated_complete_pipeline.py --step 5 --epochs 10")
            print()
    
    elapsed_time = time.time() - start_time
    
    # Summary report
    pipeline.generate_summary_report()
    
    print(f"\n⏱️  Total time: {elapsed_time:.2f}s")
    print("="*80)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Improved Quantum Algorithm ML Pipeline'
    )
    parser.add_argument(
        '--step',
        type=int,
        choices=[1, 2, 3, 4, 5],
        help='Run specific step only (1-5)'
    )
    parser.add_argument(
        '--variations',
        type=int,
        default=50,
        help='Variations per canonical implementation (default: 50)'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=10,
        help='Training epochs for CodeBERT (Step 5 only, default: 10)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=16,
        help='Batch size for CodeBERT (Step 5 only, default: 16)'
    )
    
    args = parser.parse_args()
    
    if args.step:
        pipeline = ImprovedQuantumMLPipeline()
        
        if args.step == 1:
            pipeline.step1_collect_canonical()
        elif args.step == 2:
            pipeline.step2_validate_canonical()
        elif args.step == 3:
            pipeline.step3_generate_smart_variations(args.variations)
        elif args.step == 4:
            pipeline.step4_train_multilabel_classifier()
        elif args.step == 5:
            pipeline.step5_train_codebert_classifier(
                epochs=args.epochs,
                batch_size=args.batch_size
            )
    else:
        # Pass variations to main function
        import sys
        sys.argv = ['updated_complete_pipeline.py']
        
        # Override main to use args.variations
        pipeline = ImprovedQuantumMLPipeline()
        print("╔" + "="*78 + "╗")
        print("║" + " "*15 + "IMPROVED QUANTUM ALGORITHM ML PIPELINE" + " "*24 + "║")
        print("╚" + "="*78 + "╝")
        print()
        print("This pipeline solves 3 critical problems:")
        print("  1. ✅ Uses CANONICAL implementations from trusted sources")
        print("  2. ✅ MULTI-LABEL classification (detects multiple algorithms)")
        print("  3. ✅ SMART VARIATIONS with diverse features")
        print()
        print("="*80)
        print("PIPELINE EXECUTION")
        print("="*80)
        
        start_time = time.time()
        
        canonical_count = pipeline.step1_collect_canonical()
        
        if canonical_count > 0:
            verified_count = pipeline.step2_validate_canonical()
            
            if verified_count > 0:
                variation_count = pipeline.step3_generate_smart_variations(
                    variations_per_canonical=args.variations
                )
                
                print("\n💡 To train the algorithm classifier, run:")
                print("   python updated_complete_pipeline.py --step 5 --epochs 10")
                print()
        
        elapsed_time = time.time() - start_time
        pipeline.generate_summary_report()
        print(f"\n⏱️  Total time: {elapsed_time:.2f}s")
        print("="*80)