"""
Evaluate the trained language classifier and save detailed evaluation artifacts.

Outputs are stored inside models/trained/language_classifier:
- eval_results.json
- classification_report_ensemble.txt
- confusion_matrix_eval.png
- predictions_test.jsonl
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import joblib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import torch
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from transformers import AutoModelForSequenceClassification, AutoTokenizer


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    data: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def save_json(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def evaluate(
    dataset_dir: Path,
    models_dir: Path,
    split: str,
) -> Dict[str, Any]:
    split_file = dataset_dir / f"{split}.jsonl"
    if not split_file.exists():
        raise FileNotFoundError(f"Dataset split not found: {split_file}")

    required_files = [
        models_dir / "codebert",
        models_dir / "xgboost.pkl",
        models_dir / "random_forest.pkl",
        models_dir / "gradient_boosting.pkl",
        models_dir / "tfidf.pkl",
        models_dir / "label_encoder.pkl",
        models_dir / "ensemble_weights.json",
    ]
    missing = [str(p) for p in required_files if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing trained model artifacts:\n" + "\n".join(missing)
        )

    rows = load_jsonl(split_file)
    codes = [row["code"] for row in rows]
    labels = [row["label"] for row in rows]

    label_encoder = joblib.load(models_dir / "label_encoder.pkl")
    y_true = label_encoder.transform(labels)
    class_names = list(label_encoder.classes_)

    tokenizer = AutoTokenizer.from_pretrained(str(models_dir / "codebert"))
    codebert_model = AutoModelForSequenceClassification.from_pretrained(
        str(models_dir / "codebert")
    )
    codebert_model.eval()

    xgboost_model = joblib.load(models_dir / "xgboost.pkl")
    random_forest_model = joblib.load(models_dir / "random_forest.pkl")
    gradient_boosting_model = joblib.load(models_dir / "gradient_boosting.pkl")
    tfidf = joblib.load(models_dir / "tfidf.pkl")

    with (models_dir / "ensemble_weights.json").open("r", encoding="utf-8") as f:
        ensemble_weights = json.load(f)

    print(f"Loaded {len(codes):,} samples from {split_file}")

    encodings = tokenizer(
        codes,
        truncation=True,
        padding=True,
        max_length=512,
        return_tensors="pt",
    )
    with torch.no_grad():
        outputs = codebert_model(**encodings)
        codebert_probs = torch.softmax(outputs.logits, dim=1).cpu().numpy()
    codebert_pred = np.argmax(codebert_probs, axis=1)

    x_test_tfidf = tfidf.transform(codes)
    xgb_probs = xgboost_model.predict_proba(x_test_tfidf)
    rf_probs = random_forest_model.predict_proba(x_test_tfidf)
    gb_probs = gradient_boosting_model.predict_proba(x_test_tfidf)

    xgb_pred = np.argmax(xgb_probs, axis=1)
    rf_pred = np.argmax(rf_probs, axis=1)
    gb_pred = np.argmax(gb_probs, axis=1)

    ensemble_probs = (
        ensemble_weights["codebert"] * codebert_probs
        + ensemble_weights["xgboost"] * xgb_probs
        + ensemble_weights["random_forest"] * rf_probs
        + ensemble_weights["gradient_boosting"] * gb_probs
    )
    ensemble_pred = np.argmax(ensemble_probs, axis=1)

    model_predictions = {
        "codebert": codebert_pred,
        "xgboost": xgb_pred,
        "random_forest": rf_pred,
        "gradient_boosting": gb_pred,
        "ensemble": ensemble_pred,
    }

    accuracy_by_model: Dict[str, float] = {
        model_name: float(accuracy_score(y_true, pred))
        for model_name, pred in model_predictions.items()
    }

    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true, ensemble_pred, average="macro", zero_division=0
    )
    precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(
        y_true, ensemble_pred, average="weighted", zero_division=0
    )

    report_dict = classification_report(
        y_true,
        ensemble_pred,
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )
    report_text = classification_report(
        y_true,
        ensemble_pred,
        target_names=class_names,
        zero_division=0,
    )

    cm = confusion_matrix(y_true, ensemble_pred)

    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
    )
    plt.title("Ensemble Model - Confusion Matrix (Evaluation)")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.tight_layout()
    cm_path = models_dir / "confusion_matrix_eval.png"
    plt.savefig(cm_path, dpi=300)
    plt.close()

    report_path = models_dir / "classification_report_ensemble.txt"
    report_path.write_text(report_text, encoding="utf-8")

    predictions_path = models_dir / f"predictions_{split}.jsonl"
    with predictions_path.open("w", encoding="utf-8") as f:
        for code, true_idx, pred_idx, probs in zip(codes, y_true, ensemble_pred, ensemble_probs):
            payload = {
                "true_label": class_names[int(true_idx)],
                "predicted_label": class_names[int(pred_idx)],
                "confidence": float(np.max(probs)),
                "correct": bool(int(true_idx) == int(pred_idx)),
                "probabilities": {
                    class_names[i]: float(probs[i]) for i in range(len(class_names))
                },
                "code": code,
            }
            f.write(json.dumps(payload) + "\n")

    results = {
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_split": split,
        "num_samples": len(codes),
        "classes": class_names,
        "ensemble_weights": ensemble_weights,
        "accuracy_by_model": accuracy_by_model,
        "ensemble_metrics": {
            "precision_macro": float(precision_macro),
            "recall_macro": float(recall_macro),
            "f1_macro": float(f1_macro),
            "precision_weighted": float(precision_weighted),
            "recall_weighted": float(recall_weighted),
            "f1_weighted": float(f1_weighted),
        },
        "classification_report": report_dict,
        "confusion_matrix": cm.tolist(),
        "artifacts": {
            "classification_report_text": str(report_path),
            "confusion_matrix_image": str(cm_path),
            "predictions": str(predictions_path),
        },
    }

    save_json(models_dir / "eval_results.json", results)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate trained language classifier")
    parser.add_argument(
        "--dataset-dir",
        default="datasets/language_classification",
        help="Path to dataset directory containing train/val/test jsonl files",
    )
    parser.add_argument(
        "--models-dir",
        default="models/trained/language_classifier",
        help="Path to trained language classifier artifacts",
    )
    parser.add_argument(
        "--split",
        default="test",
        choices=["train", "val", "test"],
        help="Dataset split to evaluate",
    )
    args = parser.parse_args()

    dataset_dir = Path(args.dataset_dir)
    models_dir = Path(args.models_dir)

    results = evaluate(dataset_dir=dataset_dir, models_dir=models_dir, split=args.split)

    print("\nEvaluation complete")
    print(f"Split: {results['dataset_split']}")
    print(f"Samples: {results['num_samples']:,}")
    print("\nAccuracy by model:")
    for model_name, acc in results["accuracy_by_model"].items():
        print(f"  {model_name}: {acc:.4f} ({acc * 100:.2f}%)")

    m = results["ensemble_metrics"]
    print("\nEnsemble macro scores:")
    print(f"  Precision: {m['precision_macro']:.4f}")
    print(f"  Recall:    {m['recall_macro']:.4f}")
    print(f"  F1:        {m['f1_macro']:.4f}")

    print("\nSaved:")
    print(f"  {models_dir / 'eval_results.json'}")
    print(f"  {models_dir / 'classification_report_ensemble.txt'}")
    print(f"  {models_dir / 'confusion_matrix_eval.png'}")
    print(f"  {models_dir / f'predictions_{args.split}.jsonl'}")


if __name__ == "__main__":
    main()
