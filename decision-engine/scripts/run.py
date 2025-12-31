#!/usr/bin/env python3
"""
Decision Engine FastAPI Service Runner
"""

import uvicorn
import sys
import os
from pathlib import Path

# Add parent directory (decision-engine root) to Python path
decision_engine_root = Path(__file__).parent.parent
sys.path.insert(0, str(decision_engine_root))

# Change to the decision-engine root directory
os.chdir(decision_engine_root)

# Activate virtual environment if available (for programmatic use)
def setup_virtual_env():
    """Setup virtual environment paths if available"""
    venv_paths = [".venv/bin/python", "venv/bin/python"]
    
    for venv_path in venv_paths:
        if Path(venv_path).exists():
            venv_bin = Path(venv_path).parent
            os.environ["PATH"] = f"{venv_bin}:{os.environ.get('PATH', '')}"
            os.environ["VIRTUAL_ENV"] = str(venv_bin.parent)
            print(f"🔧 Using virtual environment: {venv_bin.parent}")
            return True
    
    print("🐍 Using system Python environment")
    return False

# Setup virtual environment
setup_virtual_env()

if __name__ == "__main__":
    # Import the app and settings after adding to path
    from main import app
    from config import get_settings
    
    settings = get_settings()
    
    print("🚀 Starting Decision Engine Service...")
    print(f"📖 API Documentation available at: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"🔄 Interactive API at: http://{settings.HOST}:{settings.PORT}/redoc")
    print(f"🏥 Health check at: http://{settings.HOST}:{settings.PORT}/api/v1/decision-engine/health")
    
    uvicorn.run(
        app, 
        host=settings.HOST, 
        port=settings.PORT,
        reload=settings.DEBUG,  # Enable auto-reload during development
        log_level=settings.LOG_LEVEL.lower()
    )