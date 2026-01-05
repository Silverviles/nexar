"""Configuration settings for the application"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
MODEL_PATH = os.getenv(
    "MODEL_PATH", 
    "C:/Users/black/OneDrive/Desktop/research/nexar/ai-code-converter/codet5-quantum-best"
)

# Default settings
DEFAULT_SHOTS = 1000
DEFAULT_MAX_LENGTH = 300
DEFAULT_GATE_TYPE = "xor"

# Quantum circuit settings
DEFAULT_NUM_QUBITS = 3
HISTOGRAM_FIGSIZE = (10, 6)
CIRCUIT_STYLE = {'backgroundcolor': '#EEEEEE'}