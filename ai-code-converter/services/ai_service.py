import logging
import os

import torch
from transformers import AutoTokenizer, T5ForConditionalGeneration

logger = logging.getLogger(__name__)

MODEL_PATH = os.getenv("MODEL_PATH", "/app/models")

# Files that Hugging Face expects for a T5 model + tokenizer
_REQUIRED_FILES = {"config.json"}
_WEIGHT_FILES = {"pytorch_model.bin", "model.safetensors"}
_TOKENIZER_FILES = {"tokenizer_config.json", "spiece.model", "tokenizer.json"}


def _log_model_dir(path: str) -> set[str]:
    """Log the contents of the model directory and return the set of filenames."""
    if not os.path.isdir(path):
        logger.error("MODEL_PATH directory does not exist: %s", path)
        return set()

    files = set()
    logger.info("Model directory listing for %s:", path)
    for root, _dirs, filenames in os.walk(path):
        for fname in sorted(filenames):
            fpath = os.path.join(root, fname)
            size = os.path.getsize(fpath)
            rel = os.path.relpath(fpath, path)
            logger.info("  • %s (%s bytes)", rel, size)
            files.add(fname)

    if not files:
        logger.error("Model directory is EMPTY: %s", path)

    return files


def _validate_model_files(files: set[str]) -> None:
    """Warn about missing required model files before attempting to load."""
    for req in _REQUIRED_FILES:
        if req not in files:
            logger.error("MISSING required file: %s", req)

    if not files & _WEIGHT_FILES:
        logger.error(
            "MISSING model weights — need at least one of: %s",
            ", ".join(sorted(_WEIGHT_FILES)),
        )

    if not files & _TOKENIZER_FILES:
        logger.warning(
            "MISSING tokenizer files — need at least one of: %s. "
            "from_pretrained() may fall back to _name_or_path from config.json.",
            ", ".join(sorted(_TOKENIZER_FILES)),
        )


class AIService:
    def __init__(self):
        logger.info("Loading model from MODEL_PATH=%s", MODEL_PATH)

        present = _log_model_dir(MODEL_PATH)
        _validate_model_files(present)

        logger.info("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_PATH, local_files_only=True
        )
        logger.info("Tokenizer loaded successfully.")

        logger.info("Loading model weights...")
        self.model = T5ForConditionalGeneration.from_pretrained(
            MODEL_PATH, local_files_only=True
        )
        self.model.eval()
        logger.info("Model loaded and set to eval mode.")

    def generate_quantum_code(self, python_code: str, max_length: int = 300) -> str:
        """Generate quantum code from Python code using AI model"""
        inputs = self.tokenizer(
            f"Translate Python to quantum circuit:\n{python_code}",
            return_tensors="pt",
            truncation=True,
            max_length=256,
        )

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs, max_length=max_length, num_beams=3, do_sample=True
            )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)


# Singleton instance
ai_service = AIService()
