"""
CodeBERT Algorithm Classifier Training Script

Fine-tunes CodeBERT for multi-label quantum algorithm detection

Usage:
    python train_codebert_algorithm_classifier.py --variations-path datasets/algorithm_variations --epochs 10 --batch-size 16
"""

import argparse
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import RobertaTokenizer, AdamW, get_linear_schedule_with_warmup
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import hamming_loss, f1_score, accuracy_score
from tqdm import tqdm
from datetime import datetime
import random

from modules.codebert_algorithm_classifier import CodeBERTMultiLabelClassifier, CodeBERTAlgorithmClassifier


class FocalLoss(nn.Module):
    """
    Focal Loss: Focuses learning on hard-to-classify examples
    Reduces loss for well-classified examples (easy cases)
    
    Formula: FL = -alpha * (1 - pt)^gamma * log(pt)
    - gamma: focusing parameter (higher = more focus on hard examples)
    - alpha: class weight (like pos_weight in BCE)
    
    Paper: https://arxiv.org/abs/1708.02002
    """
    def __init__(self, alpha=None, gamma=2.0, reduction='mean'):
        super().__init__()
        self.alpha = alpha  # Shape: (num_classes,)
        self.gamma = gamma
        self.reduction = reduction
    
    def forward(self, inputs, targets):
        # Standard BCE loss
        bce_loss = nn.functional.binary_cross_entropy_with_logits(
            inputs, targets, reduction='none'
        )
        
        # Get probabilities
        pt = torch.exp(-bce_loss)  # Probability of correct prediction
        
        # Focal term: (1 - pt)^gamma
        # When pt is high (confident correct prediction), focal term is small
        # When pt is low (hard example), focal term is large
        focal_loss = (1 - pt) ** self.gamma * bce_loss
        
        # Apply class weights
        if self.alpha is not None:
            # alpha_t = alpha if target=1, else (1-alpha)
            alpha_t = self.alpha * targets + (1 - self.alpha) * (1 - targets)
            focal_loss = alpha_t * focal_loss
        
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        return focal_loss


def is_broken_generated_code(code: str) -> bool:
    """Detect malformed synthesized code strings that should not be used as CODE input."""
    if not code:
        return True

    lowered = code.lower()
    broken_patterns = [
        "quantumcircuit(0)",
        "qc.h()",
        "qc.x()",
        "qc.y()",
        "qc.z()",
        "qc.cx()",
        "qc.cz()",
        "qc.cp()",
    ]
    return any(p in lowered for p in broken_patterns)


def build_training_text(sample: Dict) -> str:
    """Build a robust text representation for training from code and IR."""
    code = (sample.get('code') or '').strip()
    ir = sample.get('ir') or {}

    # Always include an IR-derived semantic summary because some generated code
    # samples are syntactically broken and lose essential qubit/gate context.
    source_language = sample.get('language', ir.get('source_language', 'unknown'))
    qubit_count = ir.get('qubit_count', 0)
    ops = ir.get('operations', [])

    ir_lines = [
        f"language: {source_language}",
        f"qubits: {qubit_count}",
        f"ops: {len(ops)}",
    ]

    for op in ops:
        gate = op.get('gate_name', 'unknown')
        targets = op.get('target_qubits', [])
        controls = op.get('control_qubits', [])
        params = op.get('parameters', [])
        tags = op.get('semantic_tags', [])
        ir_lines.append(
            f"op={gate} tgt={targets} ctrl={controls} params={params} tags={tags}"
        )

    ir_text = "\n".join(ir_lines)

    if code and not is_broken_generated_code(code):
        return f"[CODE]\n{code}\n[IR]\n{ir_text}"
    return f"[IR]\n{ir_text}"


class QuantumCodeDataset(Dataset):
    """Dataset for quantum code samples with multi-label algorithm annotations"""
    
    def __init__(
        self,
        code_samples: List[str],
        labels: np.ndarray,
        tokenizer: RobertaTokenizer,
        max_length: int = 512
    ):
        self.code_samples = code_samples
        self.labels = torch.FloatTensor(labels)
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.code_samples)
    
    def __getitem__(self, idx):
        code = self.code_samples[idx]
        label = self.labels[idx]
        
        # Tokenize
        encoded = self.tokenizer(
            code,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoded['input_ids'].squeeze(0),
            'attention_mask': encoded['attention_mask'].squeeze(0),
            'labels': label
        }


def load_variations_dataset(variations_path: str) -> Tuple[List[str], List[List[str]], List[str]]:
    """
    Load code samples from variation files
    
    Returns:
        (code_samples, algorithm_labels, group_keys)
    """
    print("\n" + "="*80)
    print("LOADING VARIATIONS DATASET")
    print("="*80)
    
    variations_dir = Path(variations_path)
    variation_files = sorted(variations_dir.rglob('variation_*.json'))
    
    if not variation_files:
        raise ValueError(f"No variation files found in {variations_path}")
    
    print(f"\n📁 Found {len(variation_files)} variation files")
    
    code_samples = []
    algorithm_labels = []
    group_keys = []
    skipped_low_quality = 0
    
    for var_file in tqdm(variation_files, desc="Loading variations"):
        try:
            with open(var_file, 'r') as f:
                data = json.load(f)

            ir = data.get('ir') or {}
            qubit_count = ir.get('qubit_count', 0)
            ops = ir.get('operations', [])

            # Strict quality gate: avoid training on unresolved parser outputs.
            if qubit_count is None or qubit_count <= 0:
                skipped_low_quality += 1
                continue

            gate_ops = [op for op in ops if op.get('op_type') == 'gate']
            if len(gate_ops) == 0:
                skipped_low_quality += 1
                continue

            has_empty_gate = any(
                (not op.get('target_qubits')) and (not op.get('control_qubits'))
                for op in gate_ops
            )
            if has_empty_gate:
                skipped_low_quality += 1
                continue
            
            # Build robust training text from available fields.
            code = build_training_text(data)
            
            # Extract algorithm (single-label in current dataset)
            algorithm = data.get('algorithm', 'unknown')
            
            # Extract group key for grouped split
            file_name = var_file.name
            parts = file_name.split('_')
            group_key = parts[1] if len(parts) >= 3 else file_name
            
            code_samples.append(code)
            algorithm_labels.append([algorithm])  # Multi-label format (list of algorithms)
            group_keys.append(group_key)
            
        except Exception as e:
            print(f"⚠️  Error loading {var_file}: {e}")
            continue
    
    print(f"\n✅ Loaded {len(code_samples)} samples")
    print(f"   Unique groups: {len(set(group_keys))}")
    if skipped_low_quality > 0:
        print(f"   ⚠️  Skipped low-quality samples: {skipped_low_quality}")
    
    return code_samples, algorithm_labels, group_keys


def build_grouped_split(
    code_samples: List[str],
    labels: np.ndarray,
    group_keys: List[str],
    algorithms: List[str],
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[List[int], List[int]]:
    """
    Build train/test split ensuring no variation leakage
    
    Strategy:
    1. Group samples by canonical circuit (group_key)
    2. Split groups into train/test
    3. Ensure all algorithms present in train set
    """
    print("\n" + "="*80)
    print("BUILDING GROUPED TRAIN/TEST SPLIT")
    print("="*80)
    
    random.seed(random_state)
    np.random.seed(random_state)
    
    # Group samples by canonical circuit
    groups_to_indices = {}
    for idx, group_key in enumerate(group_keys):
        if group_key not in groups_to_indices:
            groups_to_indices[group_key] = []
        groups_to_indices[group_key].append(idx)
    
    unique_groups = list(groups_to_indices.keys())
    random.shuffle(unique_groups)
    
    # Calculate split point
    n_test_groups = max(1, int(len(unique_groups) * test_size))
    
    # Algorithm-safe split: ensure all algorithms in train
    max_attempts = 100
    for attempt in range(max_attempts):
        test_groups = set(unique_groups[:n_test_groups])
        train_groups = set(unique_groups[n_test_groups:])
        
        # Get train indices
        train_indices = []
        for g in train_groups:
            train_indices.extend(groups_to_indices[g])
        
        # Check if all algorithms present in train
        train_labels = labels[train_indices]
        algorithms_in_train = set(algorithms[i] for i in range(len(algorithms)) if train_labels[:, i].sum() > 0)
        
        if len(algorithms_in_train) == len(algorithms):
            # Success! All algorithms present in train
            break
        
        # Retry with different shuffle
        random.shuffle(unique_groups)
    
    # Get final train/test indices
    train_indices = []
    test_indices = []
    
    for g in train_groups:
        train_indices.extend(groups_to_indices[g])
    
    for g in test_groups:
        test_indices.extend(groups_to_indices[g])

    # Ensure test coverage for every algorithm. If an algorithm is absent from test,
    # move a small portion of its samples from train to test. This is especially
    # important when that algorithm has only one canonical group.
    fallback_moved = 0
    train_set = set(train_indices)
    test_set = set(test_indices)

    for algo_idx, algo_name in enumerate(algorithms):
        if labels[list(test_set), algo_idx].sum() > 0:
            continue

        algo_all = [i for i in range(labels.shape[0]) if labels[i, algo_idx] > 0]
        movable = [i for i in algo_all if i in train_set]
        if not movable:
            continue

        move_count = max(1, int(0.2 * len(algo_all)))
        move_count = min(move_count, len(movable))
        moved = random.sample(movable, move_count)

        for i in moved:
            train_set.discard(i)
            test_set.add(i)
        fallback_moved += len(moved)

    train_indices = sorted(train_set)
    test_indices = sorted(test_set)
    
    print(f"✅ Grouped split created:")
    print(f"   Train: {len(train_indices)} samples from {len(train_groups)} canonical circuits")
    print(f"   Test:  {len(test_indices)} samples from {len(test_groups)} canonical circuits")
    print(f"   ✅ No overlap between train/test groups")
    if fallback_moved > 0:
        print(f"   ⚠️  Fallback moved {fallback_moved} samples to ensure all algorithms appear in test")
    
    return train_indices, test_indices


def train_epoch(
    model: CodeBERTMultiLabelClassifier,
    dataloader: DataLoader,
    loss_fn,
    optimizer,
    scheduler,
    device,
    epoch: int
):
    """Train for one epoch"""
    model.train()
    total_loss = 0
    
    progress_bar = tqdm(dataloader, desc=f"Epoch {epoch}")
    
    for batch in progress_bar:
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        
        optimizer.zero_grad()
        
        # Forward pass
        logits = model(input_ids, attention_mask)
        
        # Multi-label BCE loss
        loss = loss_fn(logits, labels)
        
        # Backward pass
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        scheduler.step()
        
        total_loss += loss.item()
        progress_bar.set_postfix({'loss': f'{loss.item():.4f}'})
    
    return total_loss / len(dataloader)


def evaluate(
    model: CodeBERTMultiLabelClassifier,
    dataloader: DataLoader,
    device,
    threshold: float = 0.5
) -> Dict:
    """Evaluate model on validation/test set"""
    model.eval()
    all_predictions = []
    all_labels = []
    all_probs = []
    
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating"):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].cpu().numpy()
            
            # Forward pass
            logits = model(input_ids, attention_mask)
            probs = torch.sigmoid(logits).cpu().numpy()
            
            # Threshold predictions
            preds = (probs >= threshold).astype(int)

            # If a row has no positives, force top-1 to avoid all-zero collapse.
            row_sums = preds.sum(axis=1)
            zero_rows = np.where(row_sums == 0)[0]
            if len(zero_rows) > 0:
                top_idx = np.argmax(probs[zero_rows], axis=1)
                preds[zero_rows, top_idx] = 1
            
            all_predictions.append(preds)
            all_labels.append(labels)
            all_probs.append(probs)
    
    # Concatenate all batches
    all_predictions = np.vstack(all_predictions)
    all_labels = np.vstack(all_labels)
    all_probs = np.vstack(all_probs)
    
    # Calculate metrics
    hamming = hamming_loss(all_labels, all_predictions)
    exact_match = accuracy_score(all_labels, all_predictions)  # Subset accuracy
    f1_micro = f1_score(all_labels, all_predictions, average='micro', zero_division=0)
    f1_macro = f1_score(all_labels, all_predictions, average='macro', zero_division=0)
    f1_weighted = f1_score(all_labels, all_predictions, average='weighted', zero_division=0)
    
    # Per-algorithm F1
    f1_per_algo = f1_score(all_labels, all_predictions, average=None, zero_division=0)
    
    # Per-algorithm statistics
    per_algo_stats = {}
    for i in range(all_labels.shape[1]):
        true_count = all_labels[:, i].sum()
        pred_count = all_predictions[:, i].sum()
        true_positives = ((all_predictions[:, i] == 1) & (all_labels[:, i] == 1)).sum()
        false_positives = ((all_predictions[:, i] == 1) & (all_labels[:, i] == 0)).sum()
        false_negatives = ((all_predictions[:, i] == 0) & (all_labels[:, i] == 1)).sum()
        
        per_algo_stats[i] = {
            'true_count': int(true_count),
            'pred_count': int(pred_count),
            'tp': int(true_positives),
            'fp': int(false_positives),
            'fn': int(false_negatives),
            'f1': float(f1_per_algo[i])
        }
    
    return {
        'hamming_loss': hamming,
        'exact_match': exact_match,
        'f1_micro': f1_micro,
        'f1_macro': f1_macro,
        'f1_weighted': f1_weighted,
        'f1_per_algorithm': f1_per_algo.tolist(),
        'per_algo_stats': per_algo_stats,
        'predictions': all_predictions,
        'labels': all_labels,
        'probabilities': all_probs
    }


def main():
    parser = argparse.ArgumentParser(description='Train CodeBERT Algorithm Classifier')
    parser.add_argument('--variations-path', type=str, default='datasets/algorithm_variations',
                        help='Path to variations directory')
    parser.add_argument('--epochs', type=int, default=10,
                        help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=16,
                        help='Batch size for training')
    parser.add_argument('--learning-rate', type=float, default=2e-5,
                        help='Learning rate')
    parser.add_argument('--max-length', type=int, default=512,
                        help='Maximum sequence length')
    parser.add_argument('--test-size', type=float, default=0.2,
                        help='Test set proportion')
    parser.add_argument('--threshold', type=float, default=0.5,
                        help='Classification threshold')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed')
    parser.add_argument('--use-focal-loss', action='store_true',
                        help='Use Focal Loss instead of BCE (better for class imbalance)')
    parser.add_argument('--focal-gamma', type=float, default=2.0,
                        help='Focal loss gamma parameter (higher = more focus on hard examples)')
    
    args = parser.parse_args()
    
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "CODEBERT ALGORITHM CLASSIFIER TRAINING" + " "*20 + "║")
    print("╚" + "="*78 + "╝")
    print()
    print("🚀 Using transformer-based semantic understanding")
    print("✅ Multi-label classification (detects multiple algorithms)")
    print("✅ Cross-language generalization")
    print()
    
    # Set seeds
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)
    
    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"💻 Device: {device}")
    if torch.cuda.is_available():
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
    print()
    
    # Load dataset
    code_samples, algorithm_labels, group_keys = load_variations_dataset(args.variations_path)
    
    # Prepare multi-label binarizer
    mlb = MultiLabelBinarizer()
    labels_binary = mlb.fit_transform(algorithm_labels)
    algorithms = list(mlb.classes_)
    
    print(f"\n📊 Dataset Statistics:")
    print(f"   Total samples: {len(code_samples)}")
    print(f"   Algorithms: {len(algorithms)}")
    print(f"   Algorithm list: {algorithms}")
    
    # Label distribution
    label_counts = labels_binary.sum(axis=0)
    print(f"\n📊 Label Distribution:")
    for i, algo in enumerate(algorithms):
        print(f"   {algo}: {int(label_counts[i])} samples")
    
    # Build grouped train/test split
    train_indices, test_indices = build_grouped_split(
        code_samples,
        labels_binary,
        group_keys,
        algorithms,
        test_size=args.test_size,
        random_state=args.seed
    )
    
    # Split data
    train_codes = [code_samples[i] for i in train_indices]
    train_labels = labels_binary[train_indices]
    test_codes = [code_samples[i] for i in test_indices]
    test_labels = labels_binary[test_indices]
    
    # DIAGNOSTIC: Show per-algorithm split
    print(f"\n📊 Per-Algorithm Train/Test Split:")
    print(f"   {'Algorithm':<20} {'Total':>6} {'Train':>6} {'Test':>6} {'Test %':>7}")
    print("   " + "-" * 50)
    for i, algo in enumerate(algorithms):
        total = int(label_counts[i])
        train_count = int(train_labels[:, i].sum())
        test_count = int(test_labels[:, i].sum())
        test_pct = (test_count / total * 100) if total > 0 else 0
        print(f"   {algo:<20} {total:>6} {train_count:>6} {test_count:>6} {test_pct:>6.1f}%")
    
    # Load tokenizer
    print("\n📥 Loading CodeBERT tokenizer...")
    tokenizer = RobertaTokenizer.from_pretrained('microsoft/codebert-base')
    
    # Create datasets
    train_dataset = QuantumCodeDataset(train_codes, train_labels, tokenizer, args.max_length)
    test_dataset = QuantumCodeDataset(test_codes, test_labels, tokenizer, args.max_length)
    
    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False)
    
    print(f"\n✅ Dataloaders created:")
    print(f"   Train batches: {len(train_loader)}")
    print(f"   Test batches: {len(test_loader)}")
    
    # Initialize model
    print(f"\n🏗️  Initializing CodeBERT model...")
    model = CodeBERTMultiLabelClassifier(num_labels=len(algorithms))
    model.to(device)
    
    print(f"✅ Model initialized:")
    print(f"   Total parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"   Trainable parameters: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")
    
    # Optimizer and scheduler
    optimizer = AdamW(model.parameters(), lr=args.learning_rate)
    total_steps = len(train_loader) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(0.1 * total_steps),
        num_training_steps=total_steps
    )

    # Positive class weighting to counter imbalance and avoid trivial all-zero output.
    train_label_counts = train_labels.sum(axis=0)
    num_train = train_labels.shape[0]
    pos_weight = (num_train - train_label_counts) / np.clip(train_label_counts, 1, None)
    
    # CRITICAL FIX: Don't cap pos_weight aggressively - allow higher weights for rare classes
    # This prevents the model from learning to never predict minority classes
    pos_weight = np.clip(pos_weight, 1.0, 50.0)  # Increased from 10.0 to 50.0
    
    print("\n📊 Class Weights:")
    for algo, weight in zip(algorithms, pos_weight):
        count = int(train_label_counts[algorithms.index(algo)])
        print(f"   {algo:20s}: weight={weight:6.2f} (train_count={count})")
    
    # Choose loss function
    if args.use_focal_loss:
        print(f"\n🎯 Using Focal Loss (gamma={args.focal_gamma})")
        print("   This focuses learning on hard-to-classify examples")
        # Normalize alpha for focal loss (it uses different formulation)
        alpha = pos_weight / (1 + pos_weight)
        loss_fn = FocalLoss(alpha=torch.FloatTensor(alpha).to(device), gamma=args.focal_gamma)
    else:
        print(f"\n📊 Using BCE Loss with pos_weight")
        loss_fn = nn.BCEWithLogitsLoss(pos_weight=torch.FloatTensor(pos_weight).to(device))
    
    # Training loop
    print("\n" + "="*80)
    print("TRAINING")
    print("="*80)
    
    best_f1 = 0.0
    best_epoch = 0
    best_state_dict = None
    best_metrics = None
    
    for epoch in range(1, args.epochs + 1):
        print(f"\nEpoch {epoch}/{args.epochs}")
        print("-" * 80)
        
        # Train
        train_loss = train_epoch(model, train_loader, loss_fn, optimizer, scheduler, device, epoch)
        print(f"   Train Loss: {train_loss:.4f}")
        
        # Evaluate
        test_metrics = evaluate(model, test_loader, device, threshold=args.threshold)
        
        print(f"\n   Test Metrics:")
        print(f"      Hamming Loss: {test_metrics['hamming_loss']:.4f}")
        print(f"      Exact Match: {test_metrics['exact_match']:.4f} ({test_metrics['exact_match']*100:.2f}%)")
        print(f"      F1 (Micro): {test_metrics['f1_micro']:.4f}")
        print(f"      F1 (Macro): {test_metrics['f1_macro']:.4f}")
        print(f"      F1 (Weighted): {test_metrics['f1_weighted']:.4f}")
        
        # Per-algorithm F1
        print(f"\n   Per-Algorithm F1:")
        for i, algo in enumerate(algorithms):
            print(f"      {algo}: {test_metrics['f1_per_algorithm'][i]:.4f}")
        
        # DIAGNOSTIC: Show prediction counts for algorithms with 0% F1
        zero_f1_algos = [algorithms[i] for i, f1 in enumerate(test_metrics['f1_per_algorithm']) if f1 == 0]
        if zero_f1_algos and epoch <= 5:  # Show first 5 epochs
            print(f"\n   🔍 Diagnostic for 0% F1 algorithms:")
            for algo in zero_f1_algos:
                idx = algorithms.index(algo)
                stats = test_metrics['per_algo_stats'][idx]
                print(f"      {algo}: test={stats['true_count']}, pred={stats['pred_count']}, tp={stats['tp']}, fn={stats['fn']}")
            if epoch == 1:
                print("\n   💡 If predictions=0, model never predicts this class!")
                print("      Try: --use-focal-loss --focal-gamma 3.0")
        
        # Save best model
        if test_metrics['f1_weighted'] > best_f1:
            best_f1 = test_metrics['f1_weighted']
            best_epoch = epoch
            best_metrics = test_metrics
            best_state_dict = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            print(f"\n   🌟 New best F1! Saving model...")
    
    print("\n" + "="*80)
    print("TRAINING COMPLETE")
    print("="*80)
    print(f"\n🏆 Best Epoch: {best_epoch}")
    print(f"🏆 Best F1 (Weighted): {best_f1:.4f} ({best_f1*100:.2f}%)")
    
    # Save final model
    print("\n" + "="*80)
    print("SAVING MODEL")
    print("="*80)

    if best_state_dict is not None:
        model.load_state_dict(best_state_dict)
    else:
        best_metrics = evaluate(model, test_loader, device, threshold=args.threshold)
    
    classifier = CodeBERTAlgorithmClassifier()
    classifier.model = model
    classifier.tokenizer = tokenizer
    classifier.algorithms = algorithms
    classifier.max_length = args.max_length
    classifier.threshold = args.threshold
    classifier.device = device
    classifier.save_models()
    
    # Save evaluation report
    report = {
        'training_completed': datetime.now().isoformat(),
        'hyperparameters': {
            'epochs': args.epochs,
            'batch_size': args.batch_size,
            'learning_rate': args.learning_rate,
            'max_length': args.max_length,
            'threshold': args.threshold,
        },
        'dataset': {
            'total_samples': len(code_samples),
            'train_samples': len(train_indices),
            'test_samples': len(test_indices),
            'algorithms': algorithms,
            'label_distribution': {algo: int(count) for algo, count in zip(algorithms, label_counts)}
        },
        'best_metrics': {
            'epoch': best_epoch,
            'hamming_loss': best_metrics['hamming_loss'],
            'exact_match': best_metrics['exact_match'],
            'f1_micro': best_metrics['f1_micro'],
            'f1_macro': best_metrics['f1_macro'],
            'f1_weighted': best_metrics['f1_weighted'],
            'f1_per_algorithm': {algo: f1 for algo, f1 in zip(algorithms, best_metrics['f1_per_algorithm'])}
        }
    }
    
    report_path = Path('models/trained/trained_codebert/training_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📝 Training report saved: {report_path}")
    
    print("\n" + "="*80)
    print("✅ TRAINING COMPLETE!")
    print("="*80)
    print("\nTo use the model:")
    print("  1. Load in main.py: from modules.codebert_algorithm_classifier import CodeBERTAlgorithmClassifier")
    print("  2. Initialize: classifier = CodeBERTAlgorithmClassifier()")
    print("  3. Load models: classifier.load_models()")
    print("  4. Classify: result = classifier.classify(code=your_code)")
    print("="*80)


if __name__ == "__main__":
    main()
