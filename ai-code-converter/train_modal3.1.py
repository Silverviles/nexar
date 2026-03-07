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

MODEL = "C:/Users/black/OneDrive/Desktop/research/nexar/ai-code-converter/codet5-quantum-best-version2"
DATA = "better_datasets/python_to_quantum4.jsonl"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

tokenizer = AutoTokenizer.from_pretrained(MODEL)
model     = T5ForConditionalGeneration.from_pretrained(MODEL)
model.to(device)

# ── Dataset ────────────────────────────────────────────────
full_dataset = load_dataset("json", data_files=DATA)["train"]

split = full_dataset.train_test_split(test_size=0.2, seed=42)
dataset = DatasetDict({"train": split["train"], "validation": split["test"]})

# ── Tokenisation ───────────────────────────────────────────
# max_length=512 so HHL (~450 tokens) is never truncated mid-circuit
def tokenize(batch):
    model_inputs = tokenizer(
        batch["input"],
        truncation=True,
        padding="max_length",
        max_length=512
    )

    labels = tokenizer(
        batch["output"],
        truncation=True,
        padding="max_length",
        max_length=512
    )

    # Mask padding so it doesn't contribute to loss
    model_inputs["labels"] = [
        [(tok if tok != tokenizer.pad_token_id else -100) for tok in seq]
        for seq in labels["input_ids"]
    ]
    return model_inputs

tokenized_dataset = dataset.map(tokenize, batched=True, remove_columns=["input", "output"])

# ── Training arguments ─────────────────────────────────────
args = TrainingArguments(
    output_dir="codet5-quantum3",
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=2,      # effective batch = 8
    num_train_epochs=7,                # more epochs; early stopping will cut if needed
    logging_steps=10,
    save_strategy="epoch",
    eval_strategy="epoch",
    save_total_limit=3,
    learning_rate=5e-6,                 # lower LR → more stable fine-tune
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
    eval_dataset=tokenized_dataset["validation"],
    data_collator=DataCollatorForSeq2Seq(tokenizer, model, padding=True),
)

trainer.train()

# ── Loss curves ────────────────────────────────────────────
train_losses = [
    log["loss"] for log in trainer.state.log_history
    if "loss" in log and "eval_loss" not in log
]
eval_losses = [
    log["eval_loss"] for log in trainer.state.log_history
    if "eval_loss" in log
]

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(train_losses)
plt.xlabel("Steps")
plt.ylabel("Loss")
plt.title("Training Loss")
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.plot(eval_losses)
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.title("Validation Loss")
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("loss_curves.png", dpi=150)
plt.show()
print("Loss curves saved to loss_curves.png")

# ── Inference ──────────────────────────────────────────────
def generate_quantum_code(python_code: str, max_new_tokens: int = 512) -> str:
    """Translate a classical Python function to a Qiskit quantum circuit."""
    inputs = tokenizer(
        f"Translate Python to quantum circuit:\n{python_code}",
        return_tensors="pt",
        truncation=True,
        max_length=512,
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,  # avoids double-counting prompt length
            num_beams=4,
            do_sample=False,
            early_stopping=True,
        )

    return tokenizer.decode(outputs[0].cpu(), skip_special_tokens=True)


# ── Test with in-distribution examples ────────────────────
# (out-of-distribution examples like xor/or_gate will give garbage —
#  the model only knows the 4 trained algorithm families)
print("\n" + "="*55)
print("TESTING — in-distribution examples")
print("="*55)

test_examples = [
    # Shor
    ("SHOR",
     "def factor(n):\n"
     "    for i in range(2, int(n**0.5)+1):\n"
     "        if n % i == 0:\n"
     "            return i, n//i\n"
     "    return None"),
    # QFT
    ("QFT",
     "import math\n"
     "def dft(x):\n"
     "    N = len(x)\n"
     "    X = [0]*N\n"
     "    for k in range(N):\n"
     "        for n in range(N):\n"
     "            X[k] += x[n] * math.exp(-2j*math.pi*k*n/N)\n"
     "    return X"),
    # Simon
    ("SIMON",
     "def find_period(f, max_r):\n"
     "    for r in range(1, max_r):\n"
     "        if all(f(x) == f(x+r) for x in range(max_r - r)):\n"
     "            return r\n"
     "    return None"),
    # HHL
    ("HHL",
     "def solve_linear(A, b):\n"
     "    n = len(b)\n"
     "    for i in range(n):\n"
     "        for j in range(i+1, n):\n"
     "            factor = A[j][i] / A[i][i]\n"
     "            for k in range(i, n):\n"
     "                A[j][k] -= factor * A[i][k]\n"
     "            b[j] -= factor * b[i]\n"
     "    x = [0]*n\n"
     "    for i in range(n-1, -1, -1):\n"
     "        x[i] = b[i]\n"
     "        for j in range(i+1, n):\n"
     "            x[i] -= A[i][j] * x[j]\n"
     "        x[i] /= A[i][i]\n"
     "    return x"),
]

for label, code in test_examples:
    print(f"\n[{label}]")
    print(f"Input:\n{code}\n")
    print(f"Output:\n{generate_quantum_code(code)}")
    print("-" * 55)

# ── Save best model ────────────────────────────────────────
trainer.save_model("codet5-quantum-best-version3")
tokenizer.save_pretrained("codet5-quantum-best-version3")
print("\n✅ Best model saved to: codet5-quantum-best-version3")