#!/bin/bash
# Decision Engine - Quick Setup and Run Scripts

# Function to activate virtual environment if it exists
activate_venv() {
    if [ -f ".venv/bin/activate" ]; then
        echo "🔧 Activating virtual environment..."
        source .venv/bin/activate
    elif [ -f "venv/bin/activate" ]; then
        echo "🔧 Activating virtual environment..."
        source venv/bin/activate
    fi
}

case "$1" in
    "setup")
        echo "🚀 Running Decision Engine setup..."
        activate_venv
        python scripts/setup.py
        ;;
    "run")
        echo "🚀 Starting Decision Engine..."
        activate_venv
        python scripts/run.py
        ;;
    "dev")
        echo "🚀 Starting Decision Engine in development mode..."
        activate_venv
        DEBUG=True python scripts/run.py
        ;;
    "install")
        echo "📦 Installing dependencies..."
        activate_venv
        pip install -r requirements.txt
        ;;
    "test")
        echo "🧪 Testing health endpoint..."
        activate_venv
        sleep 2
        curl -s http://localhost:8083/api/v1/decision-engine/health | python -m json.tool
        ;;
    "venv")
        echo "🐍 Creating virtual environment..."
        python3 -m venv .venv
        echo "✅ Virtual environment created at .venv/"
        echo "💡 Run './manage.sh setup' to install dependencies"
        ;;
    "clean")
        echo "🧹 Cleaning up..."
        rm -f *.log
        rm -rf __pycache__ */__pycache__ */*/__pycache__
        rm -f decision_engine.db
        ;;
    *)
        echo "Decision Engine Management Script"
        echo "Usage: ./manage.sh [command]"
        echo ""
        echo "Commands:"
        echo "  venv     - Create virtual environment (.venv)"
        echo "  setup    - Setup environment and dependencies"
        echo "  run      - Start the service"
        echo "  dev      - Start in development mode"
        echo "  install  - Install Python dependencies"
        echo "  test     - Test the health endpoint"
        echo "  clean    - Clean temporary files"
        echo ""
        echo "Examples:"
        echo "  ./manage.sh venv     # Create virtual environment"
        echo "  ./manage.sh setup    # Setup everything"
        echo "  ./manage.sh run      # Start the service"
        ;;
esac