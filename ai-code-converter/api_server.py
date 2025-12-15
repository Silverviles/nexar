#!/usr/bin/env python3
"""
Quantum Code Converter API Backend - Qiskit 1.0+ Version
FastAPI server with /convert and /simulate endpoints
"""

import sys
import json
import time
import base64
import logging
from typing import Dict, Any, Optional
from io import BytesIO

# Third-party imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import transformers for model loading (but handle if not ready)
try:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ Transformers not available yet. Model loading disabled.")

# QISKIT 1.0+ IMPORTS
QISKIT_AVAILABLE = False
try:
    # First import matplotlib with non-interactive backend
    import matplotlib
    matplotlib.use('Agg')  # Important for server environments
    import matplotlib.pyplot as plt
    
    # Qiskit 1.0+ imports
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    from qiskit import transpile
    from qiskit.visualization import plot_histogram
    
    QISKIT_AVAILABLE = True
    print("✅ Qiskit 1.0+ and matplotlib loaded successfully!")
except ImportError as e:
    QISKIT_AVAILABLE = False
    print(f"⚠️ Import error: {e}")
    print("💡 Install with: pip install qiskit qiskit-aer matplotlib")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Quantum Code Converter API",
    description="Convert classical Python code to quantum Qiskit code and simulate it",
    version="1.0.0"
)

# Add CORS middleware (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model (loaded once at startup)
MODEL = None
TOKENIZER = None
MODEL_LOADED = False

# Constants
MAX_INPUT_LENGTH = 2048
DEFAULT_SHOTS = 1000

def load_model():
    """Load the trained model from trained_model/ directory"""
    global MODEL, TOKENIZER, MODEL_LOADED
    
    if not TRANSFORMERS_AVAILABLE:
        logger.error("Transformers library not available. Cannot load model.")
        return
    
    try:
        # Look for the actual model files
        import os
        
        # Try different possible locations
        possible_paths = [
            "trained_model/checkpoint-60",  # Checkpoint directory
            "trained_model",                # Direct model files
            "final_model",                  # Alternative location
            "./trained_model/checkpoint-60" # With relative path
        ]
        
        model_path = None
        for path in possible_paths:
            if os.path.exists(path):
                # Check if it has model files
                if os.path.exists(os.path.join(path, "config.json")):
                    model_path = path
                    logger.info(f"Found model at: {path}")
                    break
        
        if model_path is None:
            logger.error("Could not find model files in any expected location!")
            logger.info("Available directories and files:")
            for root, dirs, files in os.walk("."):
                for file in files:
                    if file.endswith((".json", ".bin", ".safetensors")):
                        logger.info(f"  {os.path.join(root, file)}")
            MODEL_LOADED = False
            return
        
        logger.info(f"Loading model from: {model_path}")
        
        # List files in the model directory
        logger.info("Files in model directory:")
        for file in os.listdir(model_path):
            logger.info(f"  - {file}")
        
        # Check the model architecture from config
        config_path = os.path.join(model_path, "config.json")
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        model_arch = config.get("architectures", [""])[0]
        logger.info(f"Model architecture: {model_arch}")
        
        # Based on the tokenizer warning, we need to load as RobertaTokenizer
        # or use AutoTokenizer which will detect the correct type
        TOKENIZER = AutoTokenizer.from_pretrained(model_path)
        
        # Try to determine what model type to use
        if model_arch:
            if "T5" in model_arch or "t5" in model_arch:
                from transformers import T5ForConditionalGeneration
                MODEL = T5ForConditionalGeneration.from_pretrained(model_path)
            elif "Roberta" in model_arch or "roberta" in model_arch:
                from transformers import RobertaForSequenceClassification
                MODEL = RobertaForSequenceClassification.from_pretrained(model_path)
            else:
                # Use AutoModel for generic loading
                MODEL = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        else:
            # Default to AutoModel if architecture unknown
            MODEL = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        
        MODEL_LOADED = True
        logger.info(f"✅ Model loaded successfully! Architecture: {model_arch}")
        
        # Test the tokenizer
        logger.info("Testing tokenizer with sample input...")
        test_input = "def add(a, b): return a + b"
        tokens = TOKENIZER(test_input, return_tensors="pt")
        logger.info(f"Tokenizer test: {len(tokens['input_ids'][0])} tokens")
        
    except Exception as e:
        logger.error(f"Failed to load model: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        logger.info("Running in demo mode - will return example quantum code")
        MODEL_LOADED = False
        
def convert_to_quantum(classical_code: str) -> str:
    """
    Convert classical Python code to quantum Qiskit code using the trained model
    """
    if not classical_code or len(classical_code.strip()) == 0:
        raise HTTPException(status_code=400, detail="Empty code provided")
    
    if len(classical_code) > MAX_INPUT_LENGTH:
        raise HTTPException(
            status_code=400, 
            detail=f"Code too long. Max length: {MAX_INPUT_LENGTH} characters"
        )
    
    # If model is loaded, use it
    if MODEL_LOADED and MODEL and TOKENIZER:
        try:
            logger.info(f"Converting classical code using trained model...")
            logger.info(f"Input: {classical_code[:100]}...")
            
            # Prepare input - adjust prompt based on how your model was trained
            prompt = f"Convert to quantum: {classical_code}"
            
            # Tokenize (handle different tokenizer types)
            try:
                inputs = TOKENIZER(
                    prompt, 
                    return_tensors="pt", 
                    max_length=512, 
                    truncation=True,
                    padding=True
                )
            except:
                # Fallback for different tokenizer types
                inputs = TOKENIZER.encode_plus(
                    prompt,
                    return_tensors="pt",
                    max_length=512,
                    truncation=True,
                    padding="max_length"
                )
            
            # Generate quantum code
            outputs = MODEL.generate(
                inputs.input_ids if hasattr(inputs, 'input_ids') else inputs['input_ids'],
                max_length=512,
                num_beams=4,
                early_stopping=True,
                temperature=0.7,
                do_sample=True
            )
            
            # Decode
            quantum_code = TOKENIZER.decode(outputs[0], skip_special_tokens=True)
            
            # Clean up the output
            quantum_code = quantum_code.strip()
            if "Convert to quantum:" in quantum_code:
                quantum_code = quantum_code.split("Convert to quantum:")[-1].strip()
            
            logger.info(f"✅ Model generated quantum code (length: {len(quantum_code)})")
            logger.info(f"Generated: {quantum_code[:100]}...")
            
            return quantum_code
            
        except Exception as e:
            logger.error(f"Model conversion failed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            # Fall back to demo mode
            logger.info("Falling back to demo mode")
    
    # DEMO MODE: Return example quantum code if model not ready
    logger.info("Using demo mode")
    
    # Simple quantum code for Qiskit 1.0+
    example_code = '''from qiskit import QuantumCircuit

    def quantum_converter():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc

    circuit = quantum_converter()'''
    
    return example_code


def simulate_quantum_code(quantum_code: str, shots: int = DEFAULT_SHOTS) -> Dict[str, Any]:

    if not QISKIT_AVAILABLE:
        raise HTTPException(
            status_code=500, 
            detail="Qiskit not available. Install with: pip install qiskit qiskit-aer"
        )
    
    if not quantum_code or len(quantum_code.strip()) == 0:
        raise HTTPException(status_code=400, detail="Empty quantum code provided")
    
    start_time = time.time()
    
    try:
        # Create a clean namespace for exec
        namespace = {}
        
        # Execute the quantum code
        exec(quantum_code, namespace)
        
        # Find QuantumCircuit object
        circuit = None
        for key, value in namespace.items():
            if isinstance(value, QuantumCircuit):
                circuit = value
                break
        
        if circuit is None:
            # Create default circuit
            circuit = QuantumCircuit(2, 2)
            circuit.h(0)
            circuit.cx(0, 1)
            circuit.measure([0, 1], [0, 1])
        
        # QISKIT 1.0+ SIMULATION
        simulator = AerSimulator()
        transpiled_circuit = transpile(circuit, simulator)
        job = simulator.run(transpiled_circuit, shots=shots)
        result = job.result()
        counts = result.get_counts()
        
        # Generate circuit diagram
        fig_circuit = circuit.draw(output='mpl')
        buf_circuit = BytesIO()
        fig_circuit.savefig(buf_circuit, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig_circuit)
        circuit_image = base64.b64encode(buf_circuit.getvalue()).decode('utf-8')
        
        # Generate histogram
        fig_hist = plot_histogram(counts)
        buf_hist = BytesIO()
        fig_hist.savefig(buf_hist, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig_hist)
        histogram_image = base64.b64encode(buf_hist.getvalue()).decode('utf-8')
        
        execution_time = time.time() - start_time
        
        logger.info(f"✅ Simulation completed in {execution_time:.2f}s")
        logger.info(f"   Shots: {shots}, Results: {counts}")
        
        return {
            "counts": counts,
            "shots": shots,
            "circuit_image": f"data:image/png;base64,{circuit_image}",
            "histogram_image": f"data:image/png;base64,{histogram_image}",
            "execution_time": f"{execution_time:.3f}s",
            "circuit_depth": circuit.depth(),
            "circuit_width": circuit.num_qubits,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Simulation error: {str(e)}"
        )

# Startup event - load model when server starts
@app.on_event("startup")
async def startup_event():
    """Load the trained model on server startup"""
    load_model()

# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Quantum Code Converter API (Qiskit 1.0+)",
        "version": "1.0.0",
        "endpoints": {
            "POST /convert": "Convert classical Python to quantum Qiskit",
            "POST /simulate": "Simulate quantum code and get results"
        },
        "model_loaded": MODEL_LOADED,
        "qiskit_available": QISKIT_AVAILABLE
    }

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": MODEL_LOADED,
        "qiskit_available": QISKIT_AVAILABLE,
        "timestamp": time.time()
    }

# Convert endpoint
@app.post("/convert")
async def convert_code(request: Dict[str, Any]):
    """
    Convert classical Python code to quantum Qiskit code
    """
    if "code" not in request:
        raise HTTPException(status_code=400, detail="Missing 'code' field in request")
    
    classical_code = request["code"]
    
    quantum_code = convert_to_quantum(classical_code)
    
    return {
        "quantum_code": quantum_code,
        "status": "success",
        "model_used": MODEL_LOADED,
        "length": len(quantum_code)
    }

# Simulate endpoint
@app.post("/simulate")
async def simulate_code(request: Dict[str, Any]):
    """
    Simulate quantum Qiskit code
    """
    if "quantum_code" not in request:
        raise HTTPException(status_code=400, detail="Missing 'quantum_code' field in request")
    
    quantum_code = request["quantum_code"]
    shots = request.get("shots", DEFAULT_SHOTS)
    
    results = simulate_quantum_code(quantum_code, shots)
    
    return results

# Example endpoint to get sample code
@app.get("/example")
async def get_example():
    """Get example classical and quantum code pairs"""
    classical_example = '''def linear_search(arr, target):
    """Classical linear search algorithm"""
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1

# Example usage
arr = [3, 7, 2, 9, 5]
target = 9
result = linear_search(arr, target)
print(f"Target found at index: {result}")'''
    
    quantum_example = '''from qiskit import QuantumCircuit

def quantum_demo_circuit():
    """Demo quantum circuit for Qiskit 1.0+"""
    qc = QuantumCircuit(3, 3)
    
    # Create superposition
    qc.h([0, 1, 2])
    
    # Create entanglement
    qc.cx(0, 1)
    qc.cx(1, 2)
    
    # Some quantum gates
    qc.rz(0.5, 0)
    qc.rz(0.5, 1)
    qc.rz(0.5, 2)
    
    # Measure
    qc.measure([0, 1, 2], [0, 1, 2])
    
    return qc

# Create circuit
circuit = quantum_demo_circuit()
print("Quantum circuit created successfully!")'''
    
    return {
        "classical": classical_example,
        "quantum": quantum_example,
        "description": "Linear search vs Quantum demo example"
    }

if __name__ == "__main__":
    # Start the server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )