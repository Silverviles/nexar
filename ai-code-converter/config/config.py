"""Configuration settings for the application"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
MODEL_PATH = os.getenv("MODEL_PATH", "/app/models")

# Default settings
DEFAULT_SHOTS = 1000
DEFAULT_MAX_LENGTH = 300
DEFAULT_GATE_TYPE = "xor"

# Quantum circuit settings
DEFAULT_NUM_QUBITS = 3
HISTOGRAM_FIGSIZE = (10, 6)
CIRCUIT_STYLE = {"backgroundcolor": "#EEEEEE"}

# Hardware Abstraction Layer (HAL) settings
HAL_URL = os.getenv("HAL_URL", "http://localhost:8004")
HAL_ENABLED = os.getenv("HAL_ENABLED", "false").lower() == "true"
HAL_DEFAULT_DEVICE = os.getenv("HAL_DEFAULT_DEVICE", "ibm_brisbane")
HAL_POLL_INTERVAL = int(os.getenv("HAL_POLL_INTERVAL", "2"))
HAL_TIMEOUT = int(os.getenv("HAL_TIMEOUT", "120"))
