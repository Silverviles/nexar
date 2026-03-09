"""
Code Analysis Engine - Complete Implementation with Accurate Analysis
Port: 8002
"""
import logging
import os

# ---------------------------------------------------------------------------
# Logging bootstrap — must run before any other imports so that every module
# that calls ``logging.getLogger(__name__)`` inherits the correct handler.
# On Cloud Run the K_SERVICE env-var is set automatically; when present we
# route all Python log records to Google Cloud Logging.  Locally we fall back
# to a human-readable stderr format.
# ---------------------------------------------------------------------------
if os.getenv("K_SERVICE"):
    import google.cloud.logging
    _log_client = google.cloud.logging.Client()
    _log_client.setup_logging()
else:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

from fastapi import FastAPI, HTTPException, APIRouter, Request
from pydantic import BaseModel
from typing import Optional
import uvicorn

# Import modules
from modules.language_detector import SupportedLanguage
from modules.ml_language_classifier import MLLanguageClassifier, ContinuousLearningManager
from modules.ast_builder import ASTBuilder
from modules.complexity_analyzer import ComplexityAnalyzer
from modules.quantum_analyzer import QuantumAnalyzer
from modules.algorithm_detector import QuantumAlgorithmDetector 
from models.analysis_result import CodeAnalysisResult, ProblemType, TimeComplexity
from modules.ml_algorithm_classifier import MLAlgorithmClassifier
from modules.codebert_algorithm_classifier import CodeBERTAlgorithmClassifier
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Code Analysis Engine",
    description="Analyzes quantum-classical code for intelligent routing",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",  # Vite dev
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # allows OPTIONS, POST, GET, etc.
    allow_headers=["*"],
)
api_router = APIRouter(prefix="/api/v1/code-analysis-engine")

# Initialize components
ml_language_classifier = MLLanguageClassifier()
learning_manager = ContinuousLearningManager()
ast_builder = ASTBuilder()
complexity_analyzer = ComplexityAnalyzer()
quantum_analyzer = QuantumAnalyzer()
algorithm_detector = QuantumAlgorithmDetector() 

# Try to load CodeBERT algorithm classifier (PRIMARY)
# Falls back to pattern matching if CodeBERT not available
codebert_classifier = None
use_codebert = False

try:
    codebert_models_dir = Path("models/trained_codebert")
    if codebert_models_dir.exists() and (codebert_models_dir / "codebert_model.pt").exists():
        print("✅ Loading CodeBERT algorithm classifier (PRIMARY MODEL)...")
        codebert_classifier = CodeBERTAlgorithmClassifier()
        codebert_classifier.load_models()
        print("✅ CodeBERT classifier loaded successfully!")
        print("   🚀 Using transformer-based semantic understanding")
        print("   ✅ Multi-label support enabled")
        use_codebert = True
    else:
        print("ℹ️  CodeBERT model not found. Train using:")
        print("      python train_codebert_algorithm_classifier.py")
        print("   📌 Falling back to pattern-based detection")
        use_codebert = False
except Exception as e:
    print(f"⚠️  Error loading CodeBERT classifier: {e}")
    print("   Falling back to pattern-based detection")
    use_codebert = False

# Load legacy classifier as fallback
ml_classifier = MLAlgorithmClassifier()
if not use_codebert:
    print("✅ Pattern-based algorithm detector loaded (FALLBACK).")

# Initialize logger
logger = logging.getLogger(__name__)

# Request Models
class CodeSubmission(BaseModel):
    code: str

class LanguageDetectionResponse(BaseModel):
    language: str
    confidence: float
    is_supported: bool
    details: str
    method: str = "fallback"  # 'ml', 'fallback', or 'error'

# Routes

@api_router.get("/")
async def root(request: Request):
    logger.info(f"[CodeAnalysisEngine] {request.method} {request.url} - Root endpoint accessed.")
    return {
        "service": "Code Analysis Engine",
        "version": "1.0.0",
        "status": "operational",
        "capabilities": [
            "Multi-language parsing",
            "Accurate complexity analysis (AST-based)",  
            "Quantum metrics extraction (state simulation)",  
            "Algorithm detection (pattern matching)",  
            "Circuit depth analysis (dependency graph)"  
        ]
    }

@api_router.get("/health")
async def health_check(request: Request):
    logger.info(f"[CodeAnalysisEngine] {request.method} {request.url} - Health check passed.")
    return {"status": "healthy", "service": "code-analysis-engine"}

@api_router.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language(submission: CodeSubmission, request: Request):
    """Detect programming language"""
    try:
        result = ml_language_classifier.detect(code=submission.code)
        logger.info(f"[CodeAnalysisEngine] {request.method} {request.url} - Detected language: {result['language']}")
        return LanguageDetectionResponse(**result)
    except Exception as e:
        logger.error(f"[CodeAnalysisEngine] {request.method} {request.url} - Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/analyze", response_model=CodeAnalysisResult)
async def analyze_code(submission: CodeSubmission, request: Request):
    """
    Complete code analysis pipeline with accurate metrics
    Returns metrics for Decision Engine
    """
    try:
        code = submission.code
        
        # Step 1: Detect language
        lang_result = ml_language_classifier.detect(code=code)
        detection_method = lang_result.get('method', 'fallback')
        
        if not lang_result["is_supported"]:
            logger.warning(f"[CodeAnalysisEngine] {request.method} {request.url} - Unsupported language: {lang_result['language']}")
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported language: {lang_result['language']}"
            )
        
        detected_lang = SupportedLanguage(lang_result["language"])
        
        # Step 2: Parse and build unified AST + canonical IR
        unified_ast = ast_builder.build(code, detected_lang)
        
        # Step 3: Determine if quantum or classical
        is_quantum = detected_lang in {
            SupportedLanguage.QISKIT, 
            SupportedLanguage.CIRQ,
            SupportedLanguage.OPENQASM,
            SupportedLanguage.QSHARP
        }
        
        classical_metrics = None
        quantum_metrics = None
        problem_type = ProblemType.CLASSICAL
        detected_algorithms = []
        algorithm_confidence = 0.0
        algorithm_detection_source = None
        
        # Metadata is always initialized, so downstream code is safe even if IR is missing.
        metadata = {
            'lines_of_code': len(code.splitlines()),
            'loop_count': 0,
            'conditional_count': 0,
            'nesting_depth': 0,
            'function_count': len(unified_ast.functions or [])
        }

        if unified_ast.canonical_ir:
            ir_meta = unified_ast.canonical_ir.metadata or {}
            metadata = {
                'lines_of_code': ir_meta.get('lines_of_code', metadata['lines_of_code']),
                'loop_count': unified_ast.canonical_ir.loop_count,
                'conditional_count': unified_ast.canonical_ir.conditional_count,
                'nesting_depth': unified_ast.canonical_ir.max_nesting_depth,
                'function_count': ir_meta.get('function_count', metadata['function_count'])
            }

        if is_quantum:
            # === QUANTUM ANALYSIS ===
            # quantum_analyzer uses:
            # - AccurateCircuitDepthCalculator
            # - QuantumStateSimulator
            quantum_metrics = quantum_analyzer.analyze(unified_ast)
            
            # Try CodeBERT first (semantic understanding), then ML, then rule-based.
            if use_codebert and codebert_classifier:
                try:
                    codebert_result = codebert_classifier.classify(code=code, threshold=0.5)

                    if codebert_result.get('algorithms'):
                        detected_algorithms = codebert_result['algorithms']
                        algorithm_confidence = codebert_result.get('confidence', 0.8)
                        algorithm_detection_source = "codebert"
                        
                        # Map primary algorithm to problem type
                        from modules.codebert_algorithm_classifier import map_algorithm_to_problem_type
                        primary_algo = detected_algorithms[0] if detected_algorithms else 'unknown'
                        problem_type = map_algorithm_to_problem_type(primary_algo)
                except Exception as e:
                    print(f"CodeBERT classification failed: {e}, falling back")

            # If CodeBERT is unavailable/failed/no result, use ML single-label classifier.
            if not detected_algorithms:
                try:
                    ml_result = ml_classifier.classify(unified_ast, quantum_metrics, use_ensemble=True)
                    ml_algorithm = ml_result.get('algorithm', 'unknown')
                    ml_confidence = float(ml_result.get('confidence', 0.0))

                    if ml_algorithm and ml_algorithm != 'unknown':
                        detected_algorithms = [ml_algorithm]
                        problem_type = ml_result.get('problem_type', ProblemType.UNKNOWN)
                        algorithm_confidence = ml_confidence
                        algorithm_detection_source = "ml-ensemble"
                except Exception as e:
                    print(f"ML classification failed: {e}, falling back")

            # If still no algorithm OR confidence is low, use accurate rule-based detector.
            if not detected_algorithms or algorithm_confidence < 0.5:
                algorithm_result = algorithm_detector.detect(unified_ast)
                problem_type = algorithm_result['problem_type']
                detected_algorithms = algorithm_result['detected_algorithms']
                algorithm_confidence = algorithm_result['confidence']
                algorithm_detection_source = "rule-based"
            
            # Final fallback to heuristics if detector confidence is still low.
            if algorithm_confidence < 0.5:
                problem_type = determine_problem_type_heuristic(code, is_quantum=True)
                algorithm_detection_source = "heuristic"
            
            # analyze classical parts if present (hybrid quantum-classical)
            if metadata['lines_of_code'] > 0 and metadata.get('function_count', 0) > 0:
                # complexity_analyzer uses:
                # - AccurateTimeComplexityAnalyzer
                # - AccurateSpaceComplexityAnalyzer
                classical_metrics = complexity_analyzer.analyze(code, metadata, unified_ast)
        else:
            # === CLASSICAL ANALYSIS ===
            # complexity_analyzer uses accurate methods
            classical_metrics = complexity_analyzer.analyze(code, metadata, unified_ast)
            problem_type = ProblemType.CLASSICAL
            algorithm_detection_source = "classical"
        
        # Step 4: Build result for Decision Engine
        result = build_analysis_result(
            detected_lang=detected_lang,
            lang_confidence=lang_result["confidence"],
            problem_type=problem_type,
            classical_metrics=classical_metrics,
            quantum_metrics=quantum_metrics,
            metadata=metadata,
            detected_algorithms=detected_algorithms,  
            algorithm_confidence=algorithm_confidence,
            algorithm_detection_source=algorithm_detection_source,
            language_detection_method=detection_method,
            code=code
        )
        
        logger.info(f"[CodeAnalysisEngine] {request.method} {request.url} - Analysis completed for code submission.")
        return result
        
    except Exception as e:
        logger.error(f"[CodeAnalysisEngine] {request.method} {request.url} - Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@api_router.get("/supported-languages")
async def get_supported_languages(request: Request):
    """List supported programming languages dynamically using LanguageDetector"""
    
    supported_languages = [lang.value for lang in SupportedLanguage if lang.value != "unknown"]

    logger.info(f"[CodeAnalysisEngine] {request.method} {request.url} - Supported languages listed.")
    return {
        "languages": [{"name": lang.capitalize(), "value": lang} for lang in supported_languages],
        "count": len(supported_languages)
    }

# Continuous learning endpoints
@api_router.post("/feedback")
async def submit_feedback(
    code: str,
    predicted: str,
    actual: str,
    confidence: float
):
    """Submit feedback for continuous learning"""
    learning_manager.collect_feedback(code, predicted, actual, confidence)
    return {"status": "feedback_received", "message": "Thank you for your feedback!"}

@api_router.post("/admin/retrain")
async def trigger_retrain():
    """Manually trigger model retraining (admin only)"""
    learning_manager._trigger_retraining()
    return {"status": "retraining_started"}

app.include_router(api_router)

# Helper Functions

def determine_problem_type_heuristic(code: str, is_quantum: bool = False) -> ProblemType:
    """
    Fallback heuristic-based problem type classification
    Used only when algorithm detector has low confidence
    """
    code_lower = code.lower()
    
    if not is_quantum:
        return ProblemType.CLASSICAL
    
    # Check for algorithm patterns (simplified)
    if 'grover' in code_lower or 'oracle' in code_lower:
        return ProblemType.SEARCH
    
    if 'vqe' in code_lower or 'qaoa' in code_lower or 'optimizer' in code_lower:
        return ProblemType.OPTIMIZATION
    
    if 'shor' in code_lower or 'factor' in code_lower:
        return ProblemType.FACTORIZATION
    
    if 'qnn' in code_lower or 'machine' in code_lower:
        return ProblemType.MACHINE_LEARNING
    
    if 'qft' in code_lower or 'fourier' in code_lower:
        return ProblemType.SAMPLING
    
    # Default for quantum circuits
    return ProblemType.SIMULATION

def build_analysis_result(
    detected_lang: SupportedLanguage,
    lang_confidence: float,
    problem_type: ProblemType,
    classical_metrics,
    quantum_metrics,
    metadata: dict,
    detected_algorithms: list = None,
    algorithm_confidence: float = 0.0,
    algorithm_detection_source: Optional[str] = None,
    language_detection_method: str = "fallback",
    code: str = ""
) -> CodeAnalysisResult:
    """Build complete analysis result with accurate metrics"""
    
    if detected_algorithms is None:
        detected_algorithms = []
    
    # Extract values for Decision Engine
    if quantum_metrics:
        qubits = quantum_metrics.qubits_required
        depth = quantum_metrics.circuit_depth  
        gates = quantum_metrics.gate_count
        cx_ratio = quantum_metrics.cx_gate_ratio
        super_score = quantum_metrics.superposition_score  
        entangle_score = quantum_metrics.entanglement_score  
        
        # Determine time complexity based on problem type
        time_comp = determine_quantum_time_complexity(problem_type, quantum_metrics)
        
        # Memory requirement for simulation
        memory_mb = quantum_analyzer.estimate_memory_requirement(qubits)
        
        is_quantum = True
        problem_size = qubits if qubits > 0 else max(metadata.get('lines_of_code', 0), 1)
        
        # Build detailed notes
        notes = (
            f"Quantum analysis: {detected_lang.value} | "
            f"{qubits} qubits | Depth: {depth} (accurate) | "
            f"Superposition: {super_score:.2f} (simulated) | "
            f"Entanglement: {entangle_score:.2f} (simulated)"
        )
        
        if detected_algorithms:
            notes += f" | Detected: {', '.join(detected_algorithms)}"
        
        # Use algorithm confidence if available, otherwise language confidence
        confidence = max(algorithm_confidence, lang_confidence)
        
    else:
        # Classical code
        qubits = 0
        depth = 0
        gates = 0
        cx_ratio = 0.0
        super_score = 0.0
        entangle_score = 0.0
        
        # Time/space complexity from complexity_analyzer
        time_comp = classical_metrics.time_complexity if classical_metrics else TimeComplexity.LINEAR
        space_comp = classical_metrics.space_complexity if classical_metrics else "O(1)"
        
        # Estimate memory from space complexity
        memory_mb = estimate_classical_memory(space_comp)
        
        is_quantum = False
        problem_size = metadata.get('lines_of_code', 1)
        
        notes = (
            f"Classical analysis: {detected_lang.value} | "
            f"{metadata.get('lines_of_code', 0)} LOC | "
            f"Time: {time_comp.value} (accurate) | "
            f"Space: {space_comp} (accurate)"
        )
        
        confidence = lang_confidence
    
    # Generate UI enhancement fields
    code_quality = calculate_code_quality_metrics(
        classical_metrics, quantum_metrics, problem_type, is_quantum, metadata
    )
    suggestions = generate_optimization_suggestions(
        classical_metrics, quantum_metrics, problem_type, is_quantum, detected_algorithms
    )
    ast_struct = generate_ast_structure(code=code, detected_lang=detected_lang, metadata=metadata)
    
    return CodeAnalysisResult(
        detected_language=detected_lang.value,
        language_confidence=lang_confidence,
        problem_type=problem_type,
        problem_size=problem_size,
        
        # Detailed metrics
        classical_metrics=classical_metrics,
        quantum_metrics=quantum_metrics,
        
        # Unified fields (for Decision Engine)
        qubits_required=qubits,
        circuit_depth=depth,
        gate_count=gates,
        cx_gate_ratio=cx_ratio,
        superposition_score=super_score,
        entanglement_score=entangle_score,
        time_complexity=time_comp,
        memory_requirement_mb=memory_mb,
        
        is_quantum=is_quantum,
        confidence_score=confidence,
        analysis_notes=notes,
        detected_algorithms=detected_algorithms,
        algorithm_detection_source=algorithm_detection_source,
        language_detection_method=language_detection_method,
        
        # UI enhancement fields
        code_quality_metrics=code_quality,
        optimization_suggestions=suggestions,
        ast_structure=ast_struct
    )

def determine_quantum_time_complexity(
    problem_type: ProblemType, 
    quantum_metrics
) -> TimeComplexity:
    """
    Determine time complexity for quantum algorithms based on problem type
    """
    # Map problem types to known quantum time complexities
    complexity_map = {
        ProblemType.SEARCH: TimeComplexity.QUANTUM_ADVANTAGE,  # O(√n) - Grover
        ProblemType.FACTORIZATION: TimeComplexity.POLYNOMIAL,   # O(n³) - Shor
        ProblemType.OPTIMIZATION: TimeComplexity.POLYNOMIAL,    # VQE/QAOA
        ProblemType.SIMULATION: TimeComplexity.POLYNOMIAL,      # Quantum simulation
        ProblemType.SAMPLING: TimeComplexity.POLYNOMIAL,        # Sampling problems
        ProblemType.MACHINE_LEARNING: TimeComplexity.POLYNOMIAL,
        ProblemType.CRYPTOGRAPHY: TimeComplexity.EXPONENTIAL,   # Some crypto is exponential
    }
    
    # Use mapping if available
    if problem_type in complexity_map:
        return complexity_map[problem_type]
    
    # Fallback: check if circuit has quantum advantage characteristics
    if quantum_metrics.has_entanglement and quantum_metrics.entanglement_score > 0.7:
        return TimeComplexity.QUANTUM_ADVANTAGE
    
    return TimeComplexity.POLYNOMIAL

def estimate_classical_memory(space_complexity: str) -> float:
    """
    Estimate memory requirement in MB from space complexity
    Assumes n=1000 for estimation
    """
    estimates = {
        'O(1)': 0.001,          # Few variables
        'O(log(n))': 0.01,      # Logarithmic data structures
        'O(n)': 8.0,            # Array of 1000 doubles (8 bytes each)
        'O(n*log(n))': 10.0,    # Slightly more than linear
        'O(n^2)': 8000.0,       # 1000x1000 matrix
        'O(n*m)': 8000.0,       # 2D array
        'O(n^3)': 8_000_000.0,  # 3D array
        'O(2^n)': 1024.0,       # Exponential (capped at reasonable size)
    }
    
    return estimates.get(space_complexity, 1.0)

def calculate_code_quality_metrics(
    classical_metrics,
    quantum_metrics,
    problem_type: ProblemType,
    is_quantum: bool,
    metadata: dict
):
    """Calculate code quality assessment"""
    from models.analysis_result import CodeQualityMetrics
    
    # Base scores
    maintainability = 100.0
    performance = 100.0
    resource_efficiency = 100.0
    
    if classical_metrics:
        # Maintainability: affected by complexity and nesting depth
        maintainability -= min(classical_metrics.cyclomatic_complexity * 2, 30)
        maintainability -= min(classical_metrics.max_nesting_depth * 5, 20)
        
        # Performance: affected by time complexity and loop count
        complexity_penalty = {
            "O(1)": 0,
            "O(log n)": 2,
            "O(n)": 5,
            "O(n log n)": 8,
            "O(n^2)": 20,
            "O(n^3)": 35,
            "O(2^n)": 50,
        }.get(classical_metrics.time_complexity.value, 15)
        performance -= complexity_penalty
        
        # Resource efficiency
        space_penalty = {
            "O(1)": 0,
            "O(n)": 5,
            "O(n^2)": 20,
            "O(n^3)": 40,
        }.get(classical_metrics.space_complexity, 10)
        resource_efficiency -= space_penalty
    
    if quantum_metrics:
        # For quantum: high circuit depth or qubit count reduces efficiency
        qubit_penalty = min(quantum_metrics.qubits_required * 2, 30)
        depth_penalty = min(quantum_metrics.circuit_depth / 10, 25)
        resource_efficiency -= qubit_penalty + depth_penalty
        
        # Good entanglement/superposition increases score
        performance += quantum_metrics.entanglement_score * 10
    
    overall = (maintainability + performance + resource_efficiency) / 3
    
    complexity_rating = "Low"
    if is_quantum:
        if quantum_metrics and quantum_metrics.gate_count > 20:
            complexity_rating = "Very High"
        elif quantum_metrics and quantum_metrics.gate_count > 10:
            complexity_rating = "High"
        elif quantum_metrics and quantum_metrics.gate_count > 5:
            complexity_rating = "Medium"
    else:
        if classical_metrics:
            if classical_metrics.cyclomatic_complexity > 15:
                complexity_rating = "Very High"
            elif classical_metrics.cyclomatic_complexity > 10:
                complexity_rating = "High"
            elif classical_metrics.cyclomatic_complexity > 5:
                complexity_rating = "Medium"
    
    return CodeQualityMetrics(
        overall_score=max(0, min(100, overall)),
        maintainability_score=max(0, min(100, maintainability)),
        performance_score=max(0, min(100, performance)),
        resource_efficiency_score=max(0, min(100, resource_efficiency)),
        code_complexity_rating=complexity_rating
    )

def generate_optimization_suggestions(
    classical_metrics,
    quantum_metrics,
    problem_type: ProblemType,
    is_quantum: bool,
    detected_algorithms: list = None
):
    """Generate actionable optimization suggestions"""
    from models.analysis_result import OptimizationSuggestion
    
    suggestions = []
    
    if not detected_algorithms:
        detected_algorithms = []
    
    if is_quantum and quantum_metrics:
        # High circuit depth
        if quantum_metrics.circuit_depth > 20:
            suggestions.append(OptimizationSuggestion(
                category="performance",
                severity="high",
                description="Circuit depth is high. Consider circuit optimization passes.",
                expected_improvement="Reduce circuit depth by 20-40%",
                estimated_savings={"circuit_depth_reduction": "20-40%"}
            ))
        
        # High gate count
        if quantum_metrics.gate_count > 30:
            suggestions.append(OptimizationSuggestion(
                category="resources",
                severity="high",
                description="High gate count increases error rates. Optimize gate decomposition.",
                expected_improvement="Reduce error accumulation",
                estimated_savings={"gate_count_reduction": "15-30%"}
            ))
        
        # Low entanglement utilization
        if quantum_metrics.entanglement_score < 0.3 and problem_type != ProblemType.CLASSICAL:
            suggestions.append(OptimizationSuggestion(
                category="structure",
                severity="medium",
                description="Limited entanglement usage. May not leverage quantum advantage.",
                expected_improvement="Better quantum resource utilization",
                estimated_savings=None
            ))
        
        # No detected algorithms
        if not detected_algorithms:
            suggestions.append(OptimizationSuggestion(
                category="structure",
                severity="medium",
                description="Could not identify standard quantum algorithm. Verify circuit structure.",
                expected_improvement="Better algorithm characterization",
                estimated_savings=None
            ))
        else:
            # Algorithm-specific suggestions
            algo_name = detected_algorithms[0].lower()
            if "grover" in algo_name:
                suggestions.append(OptimizationSuggestion(
                    category="performance",
                    severity="low",
                    description="Grover's algorithm detected. Ensure oracle is optimized.",
                    expected_improvement="5-15% speedup with oracle optimization",
                    estimated_savings={"execution_time_reduction": "5-15%"}
                ))
    
    elif classical_metrics:
        # High cyclomatic complexity
        if classical_metrics.cyclomatic_complexity > 15:
            suggestions.append(OptimizationSuggestion(
                category="structure",
                severity="high",
                description="High cyclomatic complexity. Consider refactoring into smaller functions.",
                expected_improvement="Improved maintainability and testability",
                estimated_savings={"branches": classical_metrics.cyclomatic_complexity - 10}
            ))
        
        # High nesting depth
        if classical_metrics.max_nesting_depth > 5:
            suggestions.append(OptimizationSuggestion(
                category="structure",
                severity="medium",
                description="Deep nesting detected. Refactor to reduce indentation levels.",
                expected_improvement="Better readability and reduced bugs",
                estimated_savings={"nesting_depth_reduction": "2-3 levels"}
            ))
        
        # High time complexity
        if classical_metrics.time_complexity.value in ["O(n^2)", "O(n^3)", "O(2^n)"]:
            suggestions.append(OptimizationSuggestion(
                category="performance",
                severity="high",
                description=f"Algorithm has {classical_metrics.time_complexity.value} complexity. Consider better algorithms.",
                expected_improvement="Significant performance improvement",
                estimated_savings={"speedup_factor": "5x-100x possible"}
            ))
        
        # Many loops
        if classical_metrics.loop_count > 5:
            suggestions.append(OptimizationSuggestion(
                category="performance",
                severity="medium",
                description="Multiple nested loops detected. Consider vectorization or parallel processing.",
                expected_improvement="20-50% performance improvement",
                estimated_savings={"execution_time_reduction": "20-50%"}
            ))
    
    return suggestions

def generate_ast_structure(code: str, detected_lang: SupportedLanguage, metadata: dict):
    """Generate simplified AST for visualization"""
    from models.analysis_result import ASTNode
    
    try:
        ast = ASTNode(
            type="program",
            name=detected_lang.value,
            attributes={
                "language": detected_lang.value,
                "lines_of_code": metadata.get("lines_of_code", 0),
            },
            children=[
                ASTNode(
                    type="imports",
                    children=[
                        ASTNode(
                            type="import",
                            name=imp,
                            line_number=i+1
                        ) for i, imp in enumerate(
                            code.split('\n')[0:10] if detected_lang == SupportedLanguage.PYTHON else []
                        ) if imp.strip().startswith('import' or 'from')
                    ]
                ),
                ASTNode(
                    type="functions",
                    attributes={"count": metadata.get("function_count", 0)},
                    complexity_score=metadata.get("nesting_depth", 0) / 10.0
                ),
                ASTNode(
                    type="control_flow",
                    attributes={
                        "loops": metadata.get("loop_count", 0),
                        "conditionals": metadata.get("conditional_count", 0),
                    },
                    complexity_score=(
                        metadata.get("loop_count", 0) + 
                        metadata.get("conditional_count", 0)
                    ) / 10.0
                ),
            ]
        )
        return ast
    except Exception as e:
        logger.warning(f"Error generating AST structure: {e}")
        return None

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=True)