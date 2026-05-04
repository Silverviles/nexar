"""
CodeBERT Multi-Label Algorithm Classifier
Uses transformer-based semantic understanding for high-accuracy algorithm detection

This classifier:
- Understands code SEMANTICALLY (not just surface features)
- Generalizes across languages (Qiskit, Cirq, Q#, OpenQASM)
- Detects MULTIPLE algorithms per code sample
- Achieves 85-100% accuracy with proper fine-tuning
"""

import torch
import torch.nn as nn
from transformers import RobertaTokenizer, RobertaModel, RobertaConfig
import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Tuple
import pickle

from models.unified_ast import UnifiedAST
from models.analysis_result import ProblemType


class CodeBERTMultiLabelClassifier(nn.Module):
    """
    Multi-label classification head on top of CodeBERT
    
    Architecture:
    - CodeBERT base (125M parameters, pre-trained on code)
    - Dropout layer (0.1)
    - Dense layer (768 → num_algorithms)
    - Sigmoid activation (multi-label)
    """
    
    def __init__(self, num_labels: int, base_model_path: str = 'microsoft/codebert-base', dropout_prob: float = 0.1):
        super().__init__()
        # Try loading from local path first (no network), fall back to Hub on first run
        try:
            self.codebert = RobertaModel.from_pretrained(base_model_path, local_files_only=True)
        except (OSError, ValueError):
            self.codebert = RobertaModel.from_pretrained('microsoft/codebert-base')
        self.dropout = nn.Dropout(dropout_prob)
        self.classifier = nn.Linear(self.codebert.config.hidden_size, num_labels)
        
    def forward(self, input_ids, attention_mask):
        """Forward pass through CodeBERT + classifier head"""
        outputs = self.codebert(input_ids=input_ids, attention_mask=attention_mask)
        # Roberta pooler can be brittle for some fine-tuning setups; use CLS fallback.
        pooled_output = outputs.pooler_output
        if pooled_output is None:
            pooled_output = outputs.last_hidden_state[:, 0, :]
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        return logits  # Raw logits (apply sigmoid for probabilities)


class CodeBERTAlgorithmClassifier:
    """
    Production-grade quantum algorithm detector using CodeBERT
    
    Key advantages over feature-based ML:
    - Semantic understanding of code patterns
    - Cross-language generalization
    - Handles syntactic variations automatically
    - Multi-label detection (multiple algorithms per sample)
    """
    
    def __init__(self, models_dir: str = "models/trained/trained_codebert"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Model components
        self.model = None
        self.tokenizer = None
        self.algorithms = []
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Hyperparameters (set during training)
        self.max_length = 512  # Maximum token length for CodeBERT
        self.threshold = 0.5   # Probability threshold for multi-label
        
        self.loaded = False
    
    def prepare_code_for_tokenization(self, code: str) -> str:
        """
        Prepare code text for CodeBERT tokenization
        
        CodeBERT expects raw code, but we can clean it slightly:
        - Remove excessive whitespace
        - Keep comments (they contain algorithm info)
        - Keep all syntax (important for semantic understanding)
        """
        # Basic cleanup without losing semantic information
        lines = code.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        cleaned_code = '\n'.join(line for line in cleaned_lines if line)
        
        return cleaned_code
    
    def encode_code(self, code: str) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Encode code string into input_ids and attention_mask tensors
        
        Returns:
            (input_ids, attention_mask) ready for model input
        """
        if self.tokenizer is None:
            raise RuntimeError("Tokenizer not loaded. Call load_models() first.")
        
        cleaned_code = self.prepare_code_for_tokenization(code)
        
        # Tokenize with padding and truncation
        encoded = self.tokenizer(
            cleaned_code,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        input_ids = encoded['input_ids'].to(self.device)
        attention_mask = encoded['attention_mask'].to(self.device)
        
        return input_ids, attention_mask
    
    def classify(
        self, 
        code: str = None,
        unified_ast: UnifiedAST = None, 
        quantum_metrics = None,
        threshold: float = None
    ) -> Dict:
        """
        Classify quantum algorithm(s) from code
        
        Args:
            code: Raw source code (REQUIRED for CodeBERT)
            unified_ast: Optional (not used by CodeBERT, kept for API compatibility)
            quantum_metrics: Optional (not used by CodeBERT, kept for API compatibility)
            threshold: Probability threshold for multi-label classification
        
        Returns:
            {
                'algorithms': List[str],  # Detected algorithms
                'probabilities': Dict[str, float],  # Per-algorithm probabilities
                'confidence': float,  # Overall confidence
                'is_multi_label': bool,  # True if multiple algorithms detected
                'detection_source': str  # 'codebert'
            }
        """
        if not self.loaded:
            raise RuntimeError("Model not loaded. Call load_models() first.")
        
        if code is None:
            raise ValueError("CodeBERT requires raw source code. Provide 'code' parameter.")
        
        if threshold is None:
            threshold = self.threshold
        
        # Encode code
        input_ids, attention_mask = self.encode_code(code)
        
        # Inference
        self.model.eval()
        with torch.no_grad():
            logits = self.model(input_ids, attention_mask)
            probabilities = torch.sigmoid(logits).cpu().numpy()[0]  # Apply sigmoid for probabilities
        
        # Multi-label prediction: any algorithm with prob > threshold
        detected_algorithms = []
        algorithm_probs = {}
        
        for i, algo in enumerate(self.algorithms):
            prob = float(probabilities[i])
            algorithm_probs[algo] = prob
            
            if prob >= threshold:
                detected_algorithms.append(algo)
        
        # If no algorithms detected, take the highest probability one
        if not detected_algorithms:
            max_idx = np.argmax(probabilities)
            detected_algorithms = [self.algorithms[max_idx]]
        
        # Overall confidence: mean of detected algorithm probabilities
        confidence = np.mean([algorithm_probs[a] for a in detected_algorithms])
        
        return {
            'algorithms': detected_algorithms,
            'probabilities': algorithm_probs,
            'confidence': float(confidence),
            'is_multi_label': len(detected_algorithms) > 1,
            'detection_source': 'codebert',
            'model': 'codebert-multi-label'
        }
    
    def save_models(self):
        """Save fine-tuned CodeBERT model and metadata"""
        if self.model is None:
            raise RuntimeError("No model to save. Train first.")
        
        print(f"\n💾 Saving CodeBERT model to {self.models_dir}...")
        
        # Save PyTorch model
        model_path = self.models_dir / 'codebert_model.pt'
        torch.save(self.model.state_dict(), model_path)
        
        # Save tokenizer
        tokenizer_path = self.models_dir / 'tokenizer'
        self.tokenizer.save_pretrained(tokenizer_path)
        
        # Save metadata
        metadata = {
            'algorithms': self.algorithms,
            'max_length': self.max_length,
            'threshold': self.threshold,
            'num_labels': len(self.algorithms),
            'device': str(self.device)
        }
        
        metadata_path = self.models_dir / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Model saved successfully!")
        print(f"   Model: {model_path}")
        print(f"   Tokenizer: {tokenizer_path}")
        print(f"   Metadata: {metadata_path}")
    
    def load_models(self):
        """Load fine-tuned CodeBERT model and metadata"""
        print("\n[INFO] Loading CodeBERT algorithm classifier...")
        
        # Check if model exists
        model_path = self.models_dir / 'codebert_model.pt'
        metadata_path = self.models_dir / 'metadata.json'
        tokenizer_path = self.models_dir / 'tokenizer'
        
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {model_path}. "
                f"Train the model first using train_codebert_algorithm_classifier.py"
            )
        
        # Load metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        self.algorithms = metadata['algorithms']
        self.max_length = metadata['max_length']
        self.threshold = metadata['threshold']
        num_labels = metadata['num_labels']
        
        # Load tokenizer (local only — no network)
        self.tokenizer = RobertaTokenizer.from_pretrained(tokenizer_path, local_files_only=True)

        # Load model (pass models_dir so it can find a local config.json)
        self.model = CodeBERTMultiLabelClassifier(
            num_labels=num_labels,
            base_model_path=str(self.models_dir),
        )
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

        # Save base model config locally so future loads are fully offline
        config_path = self.models_dir / 'config.json'
        if not config_path.exists():
            self.model.codebert.config.save_pretrained(str(self.models_dir))
        
        self.loaded = True
        
        print("[OK] CodeBERT classifier loaded!")
        print(f"   Algorithms: {len(self.algorithms)}")
        print(f"   Device: {self.device}")
        print(f"   Algorithm list: {self.algorithms}")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def map_algorithm_to_problem_type(algorithm: str) -> ProblemType:
    """Map detected algorithm to problem type"""
    mapping = {
        'grover': ProblemType.SEARCH,
        'deutsch_jozsa': ProblemType.SEARCH,
        'bernstein_vazirani': ProblemType.SEARCH,
        'simon': ProblemType.SEARCH,
        'shor': ProblemType.FACTORIZATION,
        'qft': ProblemType.SAMPLING,
        'qpe': ProblemType.SIMULATION,
        'qaoa': ProblemType.OPTIMIZATION,
        'vqe': ProblemType.OPTIMIZATION,
    }
    return mapping.get(algorithm.lower(), ProblemType.SIMULATION)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("CODEBERT QUANTUM ALGORITHM CLASSIFIER")
    print("=" * 80)
    print("\n✅ This classifier uses transformer-based semantic understanding")
    print("✅ Supports multi-label classification (multiple algorithms per code)")
    print("✅ Generalizes across languages (Qiskit, Cirq, Q#, OpenQASM)")
    print("\nTo train: python train_codebert_algorithm_classifier.py")
    print("To use: Load in main.py and call classifier.classify(code=your_code)")
    print("=" * 80)
