#!/usr/bin/env python3
"""
Decision Engine Setup Script
Prepares the development environment and creates necessary files
"""

import subprocess
import sys
from pathlib import Path
import json
import os

def activate_virtual_env():
    """Activate virtual environment if it exists"""
    venv_paths = [".venv/bin/activate", "venv/bin/activate"]
    
    for venv_path in venv_paths:
        if Path(venv_path).exists():
            print(f"🔧 Virtual environment found at {venv_path}")
            # Set environment variables to use the virtual environment
            venv_bin = Path(venv_path).parent
            os.environ["PATH"] = f"{venv_bin}:{os.environ.get('PATH', '')}"
            os.environ["VIRTUAL_ENV"] = str(venv_bin.parent)
            return True
    
    print("ℹ️  No virtual environment found (.venv or venv), using system Python")
    return False

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Try to use virtual environment Python if available
    python_exe = sys.executable
    venv_python = None
    
    for venv_path in [".venv/bin/python", "venv/bin/python"]:
        if Path(venv_path).exists():
            venv_python = str(Path(venv_path).absolute())
            break
    
    if venv_python:
        python_exe = venv_python
        print(f"🐍 Using virtual environment Python: {python_exe}")
    else:
        print(f"🐍 Using system Python: {python_exe}")
    
    try:
        subprocess.run([python_exe, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    return True

def create_mock_models():
    """Create mock models for development if they don't exist"""
    ml_models_dir = Path("ml_models")
    model_file = ml_models_dir / "decision_engine_model.pkl"
    scaler_file = ml_models_dir / "feature_scaler.pkl"
    
    if model_file.exists() and scaler_file.exists():
        print("🤖 ML models already exist, skipping creation...")
        return True
    
    print("🤖 Creating mock ML models...")
    try:
        # Look for create_mock_model.py in current directory or scripts directory
        mock_script = "create_mock_model.py"
        if not Path(mock_script).exists():
            mock_script = "scripts/create_mock_model.py"
        
        subprocess.run([sys.executable, mock_script], check=True)
        print("✅ Mock models created successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create mock models: {e}")
        return False
    return True

def create_env_file():
    """Create .env file from example.env template"""
    env_file = Path(".env")  # Current working directory (decision-engine root)
    example_env_file = Path("example.env")
    
    if not env_file.exists():
        if example_env_file.exists():
            print("📝 Creating .env file from example.env...")
            import shutil
            shutil.copy2(example_env_file, env_file)
            print("✅ .env file created from example.env!")
        else:
            print("❌ example.env file not found. Please create it first.")
            print(f"Current directory: {Path.cwd()}")
            print(f"Looking for: {example_env_file.absolute()}")
            return False
    else:
        print("📝 .env file already exists")
    return True

def verify_structure():
    """Verify the project structure"""
    print("🔍 Verifying project structure...")
    
    required_dirs = [
        "config", "models", "routes", "schemas", "services", "ml_models", "scripts"
    ]
    
    required_files = [
        "main.py", "requirements.txt", "scripts/run.py", "scripts/setup.py",
        "config/__init__.py", "config/app_config.py",
        "models/__init__.py", "models/decision_engine.py",
        "routes/__init__.py", "routes/decision_engine_routes.py",
        "schemas/__init__.py", "schemas/decision_engine.py", 
        "services/__init__.py", "services/decision_engine_service.py"
    ]
    
    missing = []
    
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing.append(f"Directory: {dir_name}")
    
    for file_name in required_files:
        if not Path(file_name).exists():
            missing.append(f"File: {file_name}")
    
    if missing:
        print("❌ Missing files/directories:")
        for item in missing:
            print(f"  - {item}")
        return False
    
    print("✅ Project structure verified!")
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up Decision Engine...")
    print("=" * 50)
    
    # Change to the decision-engine directory (parent of scripts)
    decision_engine_dir = Path(__file__).parent.parent
    import os
    os.chdir(decision_engine_dir)
    
    steps = [
        ("Verifying project structure", verify_structure),
        ("Activating virtual environment", activate_virtual_env),
        ("Creating .env file", create_env_file),
        ("Installing dependencies", install_dependencies),
        ("Creating mock models", create_mock_models)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("📚 Next steps:")
    print("1. Run the service: python scripts/run.py")
    print("2. Visit API docs: http://localhost:8003/docs")
    print("3. Test the health endpoint: curl http://localhost:8003/api/v1/decision-engine/health")

if __name__ == "__main__":
    main()