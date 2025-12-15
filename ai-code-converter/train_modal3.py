import json
import matplotlib.pyplot as plt
import torch
from datasets import load_dataset, DatasetDict
from transformers import (
    AutoTokenizer,
    T5ForConditionalGeneration,
    Trainer,
    TrainingArguments,
    DataCollatorForSeq2Seq
)

MODEL = "C:/Users/black/OneDrive/Desktop/research/nexar/ai-code-converter/codet5-quantum/checkpoint-450"
DATA = "better_datasets/python_to_quantum.jsonl"

# Set device (GPU if available, else CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = T5ForConditionalGeneration.from_pretrained(MODEL)

# Move model to device
model.to(device)

# Load and split dataset
full_dataset = load_dataset("json", data_files=DATA)["train"]

# Split into train (80%) and validation (20%)
train_test_split = full_dataset.train_test_split(test_size=0.2, seed=42)
dataset = DatasetDict({
    "train": train_test_split["train"],
    "validation": train_test_split["test"]
})

def tokenize(batch):
    inputs = tokenizer(batch["input"], truncation=True, padding="max_length", max_length=256)
    labels = tokenizer(batch["output"], truncation=True, padding="max_length", max_length=256)
    inputs["labels"] = labels["input_ids"]
    return inputs

# Tokenize both train and validation
tokenized_dataset = dataset.map(tokenize, batched=True)

args = TrainingArguments(
    output_dir="codet5-quantum",
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=6,
    logging_steps=10,
    save_strategy="epoch",  # Keep as epoch
    eval_strategy="epoch",  # Changed from "steps" to "epoch"
    learning_rate=5e-5,
    warmup_steps=100,
    weight_decay=0.01,
    report_to="none",
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["validation"],  # Add validation set
    data_collator=DataCollatorForSeq2Seq(tokenizer, model)
)

trainer.train()

# Plot training and validation loss
train_losses = [log["loss"] for log in trainer.state.log_history if "loss" in log and "eval_loss" not in log]
eval_losses = [log["eval_loss"] for log in trainer.state.log_history if "eval_loss" in log]

plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(train_losses)
plt.xlabel("Steps")
plt.ylabel("Loss")
plt.title("Training Loss Curve")
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.plot(eval_losses)
plt.xlabel("Evaluation Steps")
plt.ylabel("Loss")
plt.title("Validation Loss Curve")
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# ------------------------------------------------------------
# IMPROVED INFERENCE FUNCTION WITH DEVICE HANDLING
# ------------------------------------------------------------
def generate_quantum_code_improved(python_code: str):
    """Generate quantum code with proper device handling"""
    # Tokenize
    inputs = tokenizer(
        f"Translate Python to quantum circuit:\n{python_code}",
        return_tensors="pt",
        truncation=True,
        max_length=256
    )
    
    # Move inputs to same device as model
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=300,
            num_beams=4,
            do_sample=False,
            early_stopping=True
        )
    
    # Move output back to CPU for decoding
    output_text = tokenizer.decode(outputs[0].cpu(), skip_special_tokens=True)
    return output_text

# Test the improved function
print("\n" + "="*50)
print("TESTING IMPROVED INFERENCE")
print("="*50)

test_examples = [
    "def xor(a, b): return a ^ b",
    "def or_gate(x, y): return x | y",
    "def and_operation(a, b): return a & b"
]

for i, test in enumerate(test_examples, 1):
    print(f"\nTest {i}:")
    print(f"Input:  {test}")
    output = generate_quantum_code_improved(test)
    print(f"Output: {output}")
    print("-" * 40)

# Save the best model
trainer.save_model("codet5-quantum-best")
print("\n✅ Best model saved to: codet5-quantum-best")