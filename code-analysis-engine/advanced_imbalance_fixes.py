"""
Advanced fixes for 0% F1 on specific algorithms
Apply these if increasing pos_weight to 50 doesn't help
"""

# FIX 1: Use per-class thresholds (lower for classes that are never predicted)
def evaluate_with_adaptive_thresholds(model, dataloader, device, algorithms, base_threshold=0.5):
    """
    Use lower thresholds for classes that the model is hesitant to predict
    """
    import torch
    import numpy as np
    
    # First pass: get probabilities
    all_probs = []
    all_labels = []
    
    model.eval()
    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            logits = model(input_ids, attention_mask)
            probs = torch.sigmoid(logits).cpu().numpy()
            
            all_probs.append(probs)
            all_labels.append(labels.cpu().numpy())
    
    all_probs = np.vstack(all_probs)
    all_labels = np.vstack(all_labels)
    
    # Calculate per-class optimal threshold using validation set
    per_class_thresholds = []
    for i in range(all_probs.shape[1]):
        class_probs = all_probs[:, i]
        class_labels = all_labels[:, i]
        
        # Try different thresholds and pick the best F1
        best_f1 = 0
        best_thresh = base_threshold
        
        for thresh in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
            preds = (class_probs >= thresh).astype(int)
            
            tp = ((preds == 1) & (class_labels == 1)).sum()
            fp = ((preds == 1) & (class_labels == 0)).sum()
            fn = ((preds == 0) & (class_labels == 1)).sum()
            
            if tp + fp + fn == 0:
                continue
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            if f1 > best_f1:
                best_f1 = f1
                best_thresh = thresh
        
        per_class_thresholds.append(best_thresh)
        print(f"   {algorithms[i]:<20}: optimal_threshold={best_thresh:.2f} (F1={best_f1:.4f})")
    
    return per_class_thresholds


# FIX 2: Focal Loss - penalizes confident wrong predictions more
import torch
import torch.nn as nn

class FocalLoss(nn.Module):
    """
    Focal Loss focuses learning on hard examples
    Good for extreme class imbalance
    """
    def __init__(self, alpha=None, gamma=2.0, reduction='mean'):
        super().__init__()
        self.alpha = alpha  # Class weights (like pos_weight)
        self.gamma = gamma  # Focusing parameter (higher = more focus on hard examples)
        self.reduction = reduction
    
    def forward(self, inputs, targets):
        BCE_loss = nn.functional.binary_cross_entropy_with_logits(
            inputs, targets, reduction='none'
        )
        pt = torch.exp(-BCE_loss)  # Probability of correct class
        
        # Focal term: (1 - pt)^gamma reduces loss for easy examples
        focal_loss = (1 - pt) ** self.gamma * BCE_loss
        
        if self.alpha is not None:
            alpha_t = self.alpha * targets + (1 - self.alpha) * (1 - targets)
            focal_loss = alpha_t * focal_loss
        
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        return focal_loss


# FIX 3: Stratified batching - ensure every batch has rare classes
from torch.utils.data import Sampler
import numpy as np

class StratifiedBatchSampler(Sampler):
    """
    Create batches that contain samples from all classes
    Helps prevent model from ignoring rare classes
    """
    def __init__(self, labels, batch_size):
        self.labels = labels  # Shape: (n_samples, n_classes)
        self.batch_size = batch_size
        self.n_samples = len(labels)
        
        # Group samples by which classes they contain
        self.class_indices = []
        for class_idx in range(labels.shape[1]):
            indices = np.where(labels[:, class_idx] == 1)[0]
            self.class_indices.append(indices)
    
    def __iter__(self):
        # Create batches that sample from each class
        n_batches = self.n_samples // self.batch_size
        
        for _ in range(n_batches):
            batch = []
            samples_per_class = self.batch_size // len(self.class_indices)
            
            for class_indices in self.class_indices:
                if len(class_indices) > 0:
                    selected = np.random.choice(
                        class_indices,
                        size=min(samples_per_class, len(class_indices)),
                        replace=False
                    )
                    batch.extend(selected)
            
            # Fill remaining slots randomly
            while len(batch) < self.batch_size:
                batch.append(np.random.randint(0, self.n_samples))
            
            np.random.shuffle(batch)
            yield batch[:self.batch_size]
    
    def __len__(self):
        return self.n_samples // self.batch_size


# HOW TO USE THESE FIXES:

print("="*80)
print("TO USE THESE FIXES")
print("="*80)
print()
print("FIX 1 - Adaptive Thresholds:")
print("   Replace:")
print("     test_metrics = evaluate(model, test_loader, device, threshold=0.5)")
print("   With:")
print("     thresholds = evaluate_with_adaptive_thresholds(model, val_loader, device, algorithms)")
print("     test_metrics = evaluate(model, test_loader, device, per_class_thresholds=thresholds)")
print()
print("FIX 2 - Focal Loss:")
print("   Replace:")
print("     loss_fn = nn.BCEWithLogitsLoss(pos_weight=...)")
print("   With:")
print("     loss_fn = FocalLoss(alpha=pos_weight, gamma=2.0)")
print()
print("FIX 3 - Stratified Batching:")
print("   Replace:")
print("     train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)")
print("   With:")
print("     sampler = StratifiedBatchSampler(train_labels, batch_size=16)")
print("     train_loader = DataLoader(train_dataset, batch_sampler=sampler)")
