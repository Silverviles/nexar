import os
import json
import time
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import torch
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Set environment variables before other imports
os.environ["OMP_NUM_THREADS"] = "4"
os.environ["MKL_NUM_THREADS"] = "4"

from transformers import (
    T5ForConditionalGeneration,
    AutoTokenizer,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    DataCollatorForSeq2Seq,
    EarlyStoppingCallback
)
from datasets import Dataset, concatenate_datasets
from sklearn.model_selection import train_test_split
from evaluate import load

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

print("=" * 80)
print("  CODET5 QUANTUM CODE CONVERTER - TRAINING & EVALUATION")
print("=" * 80)

CONFIG = {
    'dataset_folder': 'better_datasets',
    'model_name': 'Salesforce/codet5-small',
    'pretrained_model': None,
    'output_dir': './trained_model',
    'final_model_dir': './final_model',
    'plots_dir': './training_plots',
    'reports_dir': './training_reports',

    'max_input_length': 512,
    'max_target_length': 512,

    'train_epochs': 20,
    'batch_size': 2,
    'gradient_accumulation_steps': 4,

    'learning_rate': 5e-5,
    'test_split': 0.15,
    'validation_split': 0.1,

    'gradient_checkpointing': False,
    'early_stopping_patience': 2,

    'warmup_ratio': 0.1,
    'weight_decay': 0.01,

    'log_interval': 10,
    'save_interval': 1000,
    'eval_interval': 1000,
}

class TrainingMonitor:
    def __init__(self, plots_dir):
        self.plots_dir = Path(plots_dir)
        self.plots_dir.mkdir(exist_ok=True)
        self.history = {
            'train_loss': [], 'eval_loss': [],
            'learning_rate': [], 'epoch': [],
            'bleu': [], 'rouge': [], 'exact_match': []
        }
    
    def update(self, metrics):
        for key in self.history:
            if key in metrics:
                self.history[key].append(metrics[key])
    
    def create_plots(self):
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        num_epochs = max(
            len(self.history['train_loss']),
            len(self.history['eval_loss'])
        )
        epochs = list(range(1, num_epochs + 1))
        
        # Plot 1: Training & Validation Loss
        axes[0, 0].plot(
            epochs[:len(self.history['train_loss'])],
            self.history['train_loss'],
            'b-', label='Train', linewidth=2
        )
        
        if self.history['eval_loss']:
            axes[0, 0].plot(
                epochs[:len(self.history['eval_loss'])],
                self.history['eval_loss'],
                'r-', label='Validation', linewidth=2
            )
            
        axes[0, 0].set_title('Training & Validation Loss')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: BLEU Score
        if len(self.history['bleu']) == len(epochs):
            axes[0, 1].plot(epochs, self.history['bleu'], 'g-', linewidth=2)
            axes[0, 1].set_title('BLEU Score')
            axes[0, 1].set_xlabel('Epoch')
            axes[0, 1].set_ylabel('BLEU')
            axes[0, 1].grid(True, alpha=0.3)
        else:
            axes[0, 1].text(0.5, 0.5, 'BLEU data unavailable\n(only logged during eval steps)', 
                          ha='center', va='center', transform=axes[0, 1].transAxes)
            axes[0, 1].set_title('BLEU Score')
        
        # Plot 3: Exact Match Accuracy
        if len(self.history['exact_match']) == len(epochs):
            axes[0, 2].plot(epochs, self.history['exact_match'], 'm-', linewidth=2)
            axes[0, 2].set_title('Exact Match Accuracy')
            axes[0, 2].set_xlabel('Epoch')
            axes[0, 2].set_ylabel('Accuracy')
            axes[0, 2].grid(True, alpha=0.3)
        else:
            axes[0, 2].text(0.5, 0.5, 'Exact Match data unavailable\n(only logged during eval steps)', 
                          ha='center', va='center', transform=axes[0, 2].transAxes)
            axes[0, 2].set_title('Exact Match Accuracy')
        
        # Plot 4: ROUGE-L Score
        if len(self.history['rouge']) == len(epochs):
            axes[1, 0].plot(epochs, self.history['rouge'], 'c-', linewidth=2)
            axes[1, 0].set_title('ROUGE-L Score')
            axes[1, 0].set_xlabel('Epoch')
            axes[1, 0].set_ylabel('ROUGE-L')
            axes[1, 0].grid(True, alpha=0.3)
        else:
            axes[1, 0].text(0.5, 0.5, 'ROUGE data unavailable\n(only logged during eval steps)', 
                          ha='center', va='center', transform=axes[1, 0].transAxes)
            axes[1, 0].set_title('ROUGE-L Score')
        
        # Plot 5: Learning Rate Schedule
        if self.history['learning_rate']:
            axes[1, 1].plot(epochs[:len(self.history['learning_rate'])], 
                           self.history['learning_rate'], 'y-', linewidth=2)
            axes[1, 1].set_title('Learning Rate Schedule')
            axes[1, 1].set_xlabel('Epoch')
            axes[1, 1].set_ylabel('Learning Rate')
            axes[1, 1].grid(True, alpha=0.3)
        else:
            axes[1, 1].text(0.5, 0.5, 'Learning rate data unavailable', 
                          ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Learning Rate Schedule')
        
        # Plot 6: Train vs Validation Loss
        if (self.history['train_loss'] and self.history['eval_loss'] and 
            len(self.history['train_loss']) == len(self.history['eval_loss'])):
            axes[1, 2].plot(self.history['train_loss'], self.history['eval_loss'], 'bo', alpha=0.6)
            axes[1, 2].set_title('Train vs Validation Loss')
            axes[1, 2].set_xlabel('Train Loss')
            axes[1, 2].set_ylabel('Validation Loss')
            axes[1, 2].grid(True, alpha=0.3)
        else:
            axes[1, 2].text(0.5, 0.5, 'Train/Validation loss\nlengths don\'t match', 
                          ha='center', va='center', transform=axes[1, 2].transAxes)
            axes[1, 2].set_title('Train vs Validation Loss')
        
        plt.tight_layout()
        plot_path = self.plots_dir / 'training_metrics.png'
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"📈 Training plots saved to: {plot_path}")
        
        return plot_path
        
def check_gpu():
    print("\n[STEP 1] Hardware Check...")
    
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"✅ GPU: {gpu_name}")
        print(f"   Memory: {gpu_memory:.2f} GB")
        print(f"   CUDA: {torch.version.cuda}")
        return True, 'cuda'
    else:
        print("⚠️  No GPU - Using CPU")
        return False, 'cpu'

def load_existing_dataset(existing_path='./existing_data.json'):
    """Load existing training data for retraining"""
    existing_path = Path(existing_path)
    if existing_path.exists():
        with open(existing_path, 'r') as f:
            existing_data = json.load(f)
        print(f"📂 Loaded {len(existing_data)} existing samples")
        return existing_data
    return []

def load_new_dataset(dataset_folder):
    print(f"\n[STEP 2] Loading new data from '{dataset_folder}'...")
    
    data = []
    dataset_path = Path(dataset_folder)
    
    if not dataset_path.exists():
        print(f"❌ Dataset folder not found!")
        return []
    
    categories = {}
    for category_folder in dataset_path.iterdir():
        if not category_folder.is_dir():
            continue
        
        category_count = 0
        category_name = category_folder.name
        
        for pair_folder in category_folder.iterdir():
            if not pair_folder.is_dir():
                continue
            
            classical_file = pair_folder / "classical.py"
            quantum_file = pair_folder / "quantum.py"
            
            if classical_file.exists() and quantum_file.exists():
                try:
                    with open(classical_file, 'r', encoding='utf-8') as f:
                        classical_code = f.read().strip()
                    
                    with open(quantum_file, 'r', encoding='utf-8') as f:
                        quantum_code = f.read().strip()
                    
                    if classical_code and quantum_code:
                        data.append({
                            'classical': classical_code,
                            'quantum': quantum_code,
                            'category': category_name,
                            'source': 'new',
                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                        })
                        category_count += 1
                
                except Exception:
                    continue
        
        categories[category_name] = category_count
    
    print(f"✅ New data: {len(data)} pairs")
    for cat, count in categories.items():
        print(f"   - {cat}: {count} pairs")
    
    return data

def combine_datasets(existing_data, new_data):
    """Combine existing and new data for retraining"""
    print(f"\n[STEP 3] Combining datasets...")
    
    all_data = existing_data + new_data
    
    sources = {}
    for item in all_data:
        source = item.get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1
    
    print(f"✅ Total data: {len(all_data)} pairs")
    for source, count in sources.items():
        print(f"   - {source}: {count} pairs")
    
    return all_data

def save_combined_dataset(data, output_path='./combined_data.json'):
    """Save combined dataset for future retraining"""
    output_path = Path(output_path)
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"💾 Combined dataset saved to: {output_path}")

def load_model_for_retraining(model_path, use_gpu):
    """Load existing model for retraining"""
    print(f"\n[STEP 4] Loading existing model from '{model_path}'...")
    
    try:
        if not Path(model_path).exists():
            print(f"⚠️  Model not found at {model_path}, loading base model")
            return None, None
        
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        dtype = torch.float32
        model = T5ForConditionalGeneration.from_pretrained(
            model_path,
            torch_dtype=dtype,
            use_cache=True
        )
        
        print(f"✅ Existing model loaded")
        print(f"   Model: {model_path}")
        
        return model, tokenizer
    
    except Exception as e:
        print(f"❌ Error loading existing model: {e}")
        return None, None

def load_model_and_tokenizer(use_gpu, pretrained_model_path=None):
    """Load model (either base or pretrained)"""
    if pretrained_model_path and Path(pretrained_model_path).exists():
        return load_model_for_retraining(pretrained_model_path, use_gpu)
    else:
        print(f"\n[STEP 4] Loading base model '{CONFIG['model_name']}'...")
        
        try:
            # CRITICAL FIX: Use proper T5 tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                CONFIG['model_name'],
                use_fast=True,
                model_max_length=CONFIG['max_input_length']
            )
            
            # CRITICAL: Set pad token for T5
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            print(f"✅ Tokenizer loaded")
            print(f"   Vocab size: {tokenizer.vocab_size}")
            print(f"   Pad token: {tokenizer.pad_token} (ID: {tokenizer.pad_token_id})")
            print(f"   EOS token: {tokenizer.eos_token} (ID: {tokenizer.eos_token_id})")
            
            # Load model with correct settings
            model = T5ForConditionalGeneration.from_pretrained(
                CONFIG['model_name'],
                torch_dtype=torch.float32,
                use_cache=False
            )
            
            # Ensure model config matches tokenizer
            model.config.pad_token_id = tokenizer.pad_token_id
            model.config.decoder_start_token_id = tokenizer.pad_token_id
            
            param_count = sum(p.numel() for p in model.parameters())
            print(f"✅ Base model loaded")
            print(f"   Parameters: {param_count:,}")
            print(f"   Model type: {type(model).__name__}")
            
            return model, tokenizer
        
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            import traceback
            traceback.print_exc()
            exit(1)

def test_model_capability(model, tokenizer):
    """Test if the model can generate sensible code"""
    print("\n" + "="*80)
    print("🧪 MODEL CAPABILITY TEST")
    print("="*80)
    
    # Test with simple code completion
    test_cases = [
        ("Complete the function: def add(a, b):", "Code completion"),
        ("Write a Python function that returns sum:", "Function writing"),
        ("Translate to quantum: def hello():", "Quantum context"),
    ]
    
    for prompt, test_name in test_cases:
        print(f"\n🔬 Test: {test_name}")
        print(f"Prompt: '{prompt}'")
        
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=100)
        
        with torch.no_grad():
            try:
                outputs = model.generate(
                    **inputs,
                    max_length=150,
                    num_beams=3,
                    temperature=0.7,
                    do_sample=False,  # Start with greedy
                    no_repeat_ngram_size=3,
                    early_stopping=True
                )
                
                generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
                print(f"Generated: {generated}")
                
            except Exception as e:
                print(f"❌ Generation failed: {e}")
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETE")
    print("="*80)


def preprocess_function(examples, tokenizer):
    """Preprocess function for T5 model"""
    inputs = []
    targets = []
    
    for classical, quantum in zip(examples["classical"], examples["quantum"]):
        # T5-style prompt with task prefix
        prompt = f"translate Python to Qiskit: {classical}"
        inputs.append(prompt)
        targets.append(quantum)
    
    # Tokenize inputs
    model_inputs = tokenizer(
        inputs, 
        max_length=CONFIG['max_input_length'], 
        truncation=True, 
        padding="max_length",
        return_tensors="pt" if tokenizer.is_fast else None
    )
    
    # Tokenize targets (labels)
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(
            targets, 
            max_length=CONFIG['max_target_length'], 
            truncation=True,
            padding="max_length",
            return_tensors="pt" if tokenizer.is_fast else None
        )
    
    # Replace padding token id with -100
    labels_input_ids = labels["input_ids"]
    
    if hasattr(labels_input_ids, 'tolist'):
        labels_input_ids = labels_input_ids.tolist()
    
    labels_input_ids = [
        [(lid if lid != tokenizer.pad_token_id else -100) for lid in seq]
        for seq in labels_input_ids
    ]
    
    model_inputs["labels"] = labels_input_ids
    return model_inputs



def prepare_datasets(data, tokenizer):
    print(f"\n[STEP 5] Preparing datasets...")
    
    if len(data) < 10:
        # For small datasets, use all data for training
        print(f"⚠️  Small dataset ({len(data)} samples). Using 80% train, 20% validation.")
        train_data, val_data = train_test_split(
            data, 
            test_size=0.2,
            random_state=42,
            shuffle=True
        )
        test_data = []
    else:
        train_data, temp_data = train_test_split(
            data, 
            test_size=CONFIG['test_split'] + CONFIG['validation_split'],
            random_state=42,
            shuffle=True
        )
    
        test_size = CONFIG['test_split'] / (CONFIG['test_split'] + CONFIG['validation_split'])
        val_data, test_data = train_test_split(
            temp_data,
            test_size=test_size,
            random_state=42
        )
    
    print(f"✅ Dataset split:")
    print(f"   Training: {len(train_data)} pairs")
    print(f"   Validation: {len(val_data)} pairs")
    if test_data:
        print(f"   Testing: {len(test_data)} pairs")
    else:
        print(f"   Testing: 0 pairs (small dataset)")
    
    train_dataset = Dataset.from_list(train_data)
    val_dataset = Dataset.from_list(val_data)
    test_dataset = Dataset.from_list(test_data) if test_data else Dataset.from_dict({})
    
    train_dataset = train_dataset.map(
        lambda x: preprocess_function(x, tokenizer),
        batched=True,
        remove_columns=[col for col in train_dataset.column_names if col not in ['input_ids', 'attention_mask', 'labels']]
    )
    
    val_dataset = val_dataset.map(
        lambda x: preprocess_function(x, tokenizer),
        batched=True,
        remove_columns=[col for col in val_dataset.column_names if col not in ['input_ids', 'attention_mask', 'labels']]
    )
    
    if test_data:
        test_dataset = test_dataset.map(
            lambda x: preprocess_function(x, tokenizer),
            batched=True,
            remove_columns=[col for col in test_dataset.column_names if col not in ['input_ids', 'attention_mask', 'labels']]
        )
    
    return train_dataset, val_dataset, test_dataset, test_data

class CustomTrainer(Seq2SeqTrainer):
    def __init__(self, monitor=None, compute_metrics_func=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.monitor = monitor
        self.compute_metrics_func = compute_metrics_func
    
    def log(self, logs, *args, **kwargs):
        super().log(logs, *args, **kwargs)
        
        if self.monitor:
            self.monitor.update(logs)
    
    def evaluate(self, *args, **kwargs):
        metrics = super().evaluate(*args, **kwargs)
        if self.monitor:
            self.monitor.update(metrics)
        return metrics
    
    def compute_metrics(self, eval_pred):
        if self.compute_metrics_func:
            return self.compute_metrics_func(eval_pred, self.tokenizer)
        return {}

def compute_metrics(eval_pred, tokenizer):
    predictions, labels = eval_pred
    
    if isinstance(predictions, tuple):
        pred_ids = predictions[0]
    else:
        pred_ids = predictions
    
    pred_str = tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
    
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    label_str = tokenizer.batch_decode(labels, skip_special_tokens=True)

    results = {}
    
    try:
        bleu_metric = load("bleu")
        bleu_result = bleu_metric.compute(
            predictions=pred_str,
            references=[[l] for l in label_str]
        )
        results["bleu"] = bleu_result["bleu"]
    except:
        results["bleu"] = 0.0
    
    exact_match = np.mean([
        p.strip() == l.strip()
        for p, l in zip(pred_str, label_str)
    ])
    results["exact_match"] = exact_match
    
    try:
        rouge_metric = load("rouge")
        rouge_result = rouge_metric.compute(
            predictions=pred_str,
            references=label_str
        )
        results["rouge"] = rouge_result["rougeL"]
    except:
        results["rouge"] = 0.0
    
    return results

def train_model(model, tokenizer, train_dataset, val_dataset, monitor):
    print(f"\n[STEP 6] Starting {'re-' if CONFIG['pretrained_model'] else ''}training...")
    
    training_args = Seq2SeqTrainingArguments(
        output_dir=CONFIG['output_dir'],
        num_train_epochs=CONFIG['train_epochs'],
        per_device_train_batch_size=CONFIG['batch_size'],
        per_device_eval_batch_size=CONFIG['batch_size'],
        gradient_accumulation_steps=CONFIG['gradient_accumulation_steps'],
        learning_rate=CONFIG['learning_rate'],
        weight_decay=CONFIG['weight_decay'],
        warmup_ratio=CONFIG['warmup_ratio'],
        eval_strategy="steps",
        eval_steps=50,  # Evaluate every 50 steps
        save_strategy="steps",
        save_steps=100,  # Save every 100 steps
        logging_dir='./logs',
        logging_steps=10,
        logging_first_step=True,
        fp16=False,
        dataloader_num_workers=2,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        report_to="none",
        disable_tqdm=False,
        gradient_checkpointing=False,
        prediction_loss_only=False,
        predict_with_generate=True,
        generation_max_length=CONFIG['max_target_length'],
        generation_num_beams=1,
        remove_unused_columns=True,
        label_names=["labels"],  
    )
    
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        padding=True
    )
    
    trainer = CustomTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
        monitor=monitor,
        compute_metrics_func=compute_metrics,
        callbacks=[
            EarlyStoppingCallback(
                early_stopping_patience=CONFIG['early_stopping_patience'],
                early_stopping_threshold=0.001
            )
        ]
    )
    
    start_time = time.time()
    
    try:
        train_result = trainer.train()
        
        training_time = time.time() - start_time
        hours = int(training_time // 3600)
        minutes = int((training_time % 3600) // 60)
        
        print(f"\n{'=' * 80}")
        print(f"✅ Training complete in {hours}h {minutes}m")
        
        metrics = train_result.metrics
        print(f"\n📊 Training Metrics:")
        train_loss = metrics.get("train_loss")
        print(f"   Final Train Loss: {train_loss:.4f}" if train_loss is not None else "   Final Train Loss: N/A")
        eval_loss = metrics.get("eval_loss")
        print(f"   Final Eval Loss: {eval_loss:.4f}" if eval_loss is not None else "   Final Eval Loss: N/A")
        
        return trainer, metrics
    
    except Exception as e:
        print(f"\n❌ Training error: {e}")
        raise

def generate_evaluation_report(model, tokenizer, test_dataset, test_data, eval_results):
    """Generate comprehensive evaluation report with plots"""
    reports_dir = Path(CONFIG['reports_dir'])
    reports_dir.mkdir(exist_ok=True)
    
    print(f"\n[STEP 7] Generating evaluation report...")
    
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'model_info': {
            'base_model': CONFIG['model_name'],
            'pretrained_model': CONFIG['pretrained_model'],
            'parameters': sum(p.numel() for p in model.parameters()),
        },
        'training_config': {
            'epochs': CONFIG['train_epochs'],
            'batch_size': CONFIG['batch_size'],
            'learning_rate': CONFIG['learning_rate'],
            'dataset_size': len(test_data) if test_data else 0,
        },
        'evaluation_metrics': eval_results,
        'sample_predictions': []
    }
    
    model.eval()
    
    print(f"\n📝 Generating sample predictions...")
    
    # Only generate predictions if we have test data
    sample_count = min(5, len(test_data)) if test_data else 0
    for i in range(sample_count):
        item = test_data[i]
        
        input_text = f"translate Python to Qiskit: {item['classical']}"

        
        inputs = tokenizer(
            input_text,
            return_tensors="pt",
            max_length=CONFIG['max_input_length'],
            truncation=True,
            padding=True
        )
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=CONFIG['max_target_length'],
                num_beams=1,
                temperature=0.7,
                early_stopping=True
            )
        
        prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        report['sample_predictions'].append({
            'input': item['classical'][:200] + ('...' if len(item['classical']) > 200 else ''),
            'expected': item['quantum'][:200] + ('...' if len(item['quantum']) > 200 else ''),
            'generated': prediction[:200] + ('...' if len(prediction) > 200 else ''),
            'category': item.get('category', 'unknown'),
            'exact_match': prediction.strip() == item['quantum'].strip()
        })
    
    report_path = reports_dir / f'evaluation_report_{time.strftime("%Y%m%d_%H%M%S")}.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"📄 Evaluation report saved to: {report_path}")
    
    generate_html_report(report, reports_dir)
    
    return report

def generate_html_report(report, reports_dir):
    """Generate HTML report for easy viewing"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Quantum Code Converter - Evaluation Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
            h2 {{ color: #34495e; margin-top: 30px; }}
            .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
            .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #3498db; }}
            .metric-value {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
            .metric-label {{ color: #7f8c8d; margin-top: 5px; }}
            .sample {{ background: #f8f9fa; padding: 15px; margin: 15px 0; border-radius: 5px; border: 1px solid #ddd; }}
            .code {{ background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; margin: 10px 0; }}
            .match-true {{ color: #27ae60; font-weight: bold; }}
            .match-false {{ color: #e74c3c; font-weight: bold; }}
            .timestamp {{ color: #7f8c8d; font-size: 14px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧬 Quantum Code Converter - Evaluation Report</h1>
            <div class="timestamp">Generated: {report['timestamp']}</div>
            
            <h2>📊 Model Information</h2>
            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-value">{report['model_info']['parameters']:,}</div>
                    <div class="metric-label">Parameters</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{report['training_config']['dataset_size']}</div>
                    <div class="metric-label">Test Samples</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{report['training_config']['epochs']}</div>
                    <div class="metric-label">Epochs</div>
                </div>
            </div>
            
            <h2>📈 Evaluation Metrics</h2>
            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-value">{report['evaluation_metrics'].get('exact_match', 0):.2%}</div>
                    <div class="metric-label">Exact Match</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{report['evaluation_metrics'].get('bleu', 0):.4f}</div>
                    <div class="metric-label">BLEU Score</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{report['evaluation_metrics'].get('rouge', 0):.4f}</div>
                    <div class="metric-label">ROUGE-L</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{report['evaluation_metrics'].get('function_match', 0):.2%}</div>
                    <div class="metric-label">Function Match</div>
                </div>
            </div>
    """
    
    if report['sample_predictions']:
        html_content += "<h2>🔍 Sample Predictions</h2>"
        for i, sample in enumerate(report['sample_predictions']):
            match_class = "match-true" if sample['exact_match'] else "match-false"
            match_text = "✓ MATCH" if sample['exact_match'] else "✗ NO MATCH"
            
            html_content += f"""
                <div class="sample">
                    <h3>Sample #{i+1} <span class="{match_class}">{match_text}</span></h3>
                    <p><strong>Category:</strong> {sample['category']}</p>
                    
                    <p><strong>Input (Classical):</strong></p>
                    <div class="code">{sample['input']}</div>
                    
                    <p><strong>Expected (Quantum):</strong></p>
                    <div class="code">{sample['expected']}</div>
                    
                    <p><strong>Generated (Quantum):</strong></p>
                    <div class="code">{sample['generated']}</div>
                </div>
            """
    
    html_content += f"""
            <h2>📋 Training Configuration</h2>
            <div class="code">
    """
    
    for key, value in report['training_config'].items():
        html_content += f"{key}: {value}\n"
    
    html_content += """
            </div>
            
            <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #eee; color: #7f8c8d; font-size: 12px;">
                <p>Generated automatically by Quantum Code Converter Training Script</p>
                <p>Check training_plots/ for visualization graphs</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    html_path = reports_dir / f'evaluation_report_{time.strftime("%Y%m%d_%H%M%S")}.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"🌐 HTML report saved to: {html_path}")

def evaluate_final_model(model, tokenizer, test_data):
    print(f"\n[STEP 8] Final evaluation on test samples...")
    
    if not test_data:
        print("⚠️  No test data available for evaluation")
        return {
            'exact_match': 0.0,
            'bleu': 0.0,
            'rouge': 0.0,
            'function_match': 0.0
        }
    
    all_predictions = []
    all_references = []
    
    model.eval()
    
    sample_count = min(50, len(test_data))
    print(f"Evaluating {sample_count} samples...")
    
    for i, item in enumerate(test_data[:sample_count]):
        input_text = f"translate Python to Qiskit: {item['classical']}"

        
        inputs = tokenizer(
            input_text,
            return_tensors="pt",
            max_length=CONFIG['max_input_length'],
            truncation=True,
            padding=True
        )
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=CONFIG['max_target_length'],
                num_beams=1,
                temperature=0.7,
                early_stopping=True
            )
        
        prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)
        all_predictions.append(prediction)
        all_references.append(item['quantum'])
    
    results = {}
    
    exact_matches = sum(1 for pred, ref in zip(all_predictions, all_references) if pred.strip() == ref.strip())
    results['exact_match'] = exact_matches / len(all_predictions)
    
    try:
        bleu = load("bleu")
        bleu_results = bleu.compute(predictions=all_predictions, references=[[r] for r in all_references])
        results['bleu'] = bleu_results['bleu']
    except:
        results['bleu'] = 0.0
    
    try:
        rouge = load("rouge")
        rouge_results = rouge.compute(predictions=all_predictions, references=all_references)
        results['rouge'] = rouge_results['rougeL']
    except:
        results['rouge'] = 0.0
    
    function_matches = 0
    for pred, ref in zip(all_predictions, all_references):
        pred_funcs = set([line.split('def ')[1].split('(')[0] for line in pred.split('\n') if 'def ' in line])
        ref_funcs = set([line.split('def ')[1].split('(')[0] for line in ref.split('\n') if 'def ' in line])
        if pred_funcs == ref_funcs:
            function_matches += 1
    
    results['function_match'] = function_matches / len(all_predictions) if all_predictions else 0.0
    
    print(f"\n{'=' * 60}")
    print("FINAL EVALUATION RESULTS")
    print('=' * 60)
    print(f"Exact Match:    {results['exact_match']:.2%}")
    print(f"BLEU Score:     {results['bleu']:.4f}")
    print(f"ROUGE-L:        {results['rouge']:.4f}")
    print(f"Function Match: {results['function_match']:.2%}")
    print(f"{'=' * 60}")
    
    return results

def save_final_model(trainer, tokenizer, eval_results, monitor):
    print(f"\n[STEP 9] Saving final model...")
    
    output_dir = Path(CONFIG['final_model_dir'])
    output_dir.mkdir(exist_ok=True)
    
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    plot_path = monitor.create_plots()
    
    model_info = {
        'model_name': CONFIG['model_name'],
        'pretrained_source': CONFIG['pretrained_model'] or 'base_model',
        'training_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'training_epochs': CONFIG['train_epochs'],
        'batch_size': CONFIG['batch_size'],
        'learning_rate': CONFIG['learning_rate'],
        'dataset_size': len(trainer.train_dataset),
        'evaluation_metrics': eval_results,
        'training_history': monitor.history,
        'plots_path': str(plot_path),
        'config': CONFIG,
    }
    
    with open(output_dir / 'model_info.json', 'w') as f:
        json.dump(model_info, f, indent=2, default=str)
    
    print(f"✅ Model saved to: {output_dir}")
    print(f"   Model info: {output_dir}/model_info.json")
    print(f"   Training plots: {plot_path}")

def main():
    print("\n" + "="*80)
    print("QUANTUM CODE CONVERTER - TRAINING MANAGER")
    print("="*80)
    print("\nOptions:")
    print("1. Train new model from scratch")
    print("2. Retrain existing model with new data")
    print("3. Continue training from checkpoint")
    
    choice = input("\nSelect option (1/2/3, default=1): ").strip() or "1"
    
    start_time = time.time()
    use_gpu, device = check_gpu()
    
    monitor = TrainingMonitor(CONFIG['plots_dir'])
    
    existing_data = []
    
    if choice in ["2", "3"]:
        existing_model = input("Path to existing model (or press Enter for ./final_model): ").strip()
        CONFIG['pretrained_model'] = existing_model or './final_model'
        
        if choice == "2":
            existing_data_path = input("Path to existing data JSON (or press Enter for auto-load): ").strip()
            if existing_data_path:
                existing_data = load_existing_dataset(existing_data_path)
            elif Path('./existing_data.json').exists():
                existing_data = load_existing_dataset('./existing_data.json')
    
    new_data = load_new_dataset(CONFIG['dataset_folder'])
    
    if not new_data and not existing_data:
        print("❌ No data found! Cannot train.")
        return
    
    if choice == "2" and existing_data:
        all_data = combine_datasets(existing_data, new_data)
        save_combined_dataset(all_data)
    else:
        all_data = new_data if new_data else existing_data

   

    model, tokenizer = load_model_and_tokenizer(use_gpu, CONFIG['pretrained_model'])
    


    train_dataset, val_dataset, test_dataset, test_data = prepare_datasets(all_data, tokenizer)
    
    debug_dataset_samples(tokenizer, train_dataset, num_samples=2)

    trainer, train_metrics = train_model(model, tokenizer, train_dataset, val_dataset, monitor)
    
    eval_results = evaluate_final_model(trainer.model, tokenizer, test_data)
    
    report = generate_evaluation_report(trainer.model, tokenizer, test_dataset, test_data, eval_results)
    
    save_final_model(trainer, tokenizer, eval_results, monitor)
    
    total_time = time.time() - start_time
    hours = int(total_time // 3600)
    minutes = int((total_time % 3600) // 60)
    
    print(f"\n{'='*80}")
    print("🎉 TRAINING COMPLETE!")
    print(f"{'='*80}")
    print(f"\n✅ Model saved: {CONFIG['final_model_dir']}")
    print(f"⏱️  Total time: {hours}h {minutes}m")
    print(f"📊 Evaluation:")
    print(f"   Exact Match: {eval_results['exact_match']:.2%}")
    print(f"   BLEU: {eval_results['bleu']:.4f}")
    print(f"   ROUGE-L: {eval_results['rouge']:.4f}")
    print(f"\n📈 View training plots: {CONFIG['plots_dir']}/training_metrics.png")
    print(f"📄 View HTML report: {CONFIG['reports_dir']}/")
    print(f"{'='*80}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()