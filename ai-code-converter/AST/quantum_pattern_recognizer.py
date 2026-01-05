"""
AI CODE CONVERTER API
Integrates AST Pattern Recognizer for Quantum Suitability Analysis
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import ast
import json
from typing import Dict, List, Any
import traceback

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class QuantumPatternRecognizer:
    """AST-based pattern recognizer for quantum-amenable algorithms."""
    
    QUANTUM_MAPPINGS = {
        'linear_search': {
            'quantum_algo': 'Grover Search',
            'speedup': 'O(√n) vs O(n)',
            'suitability_score': 0.9
        },
        'binary_search': {
            'quantum_algo': 'Quantum Binary Search',
            'speedup': 'O(log n) with better constants',
            'suitability_score': 0.7
        },
        'brute_force_optimization': {
            'quantum_algo': 'QAOA (Quantum Approximate Optimization Algorithm)',
            'speedup': 'Quadratic speedup for combinatorial problems',
            'suitability_score': 0.85
        },
        'min_max_problem': {
            'quantum_algo': 'Quantum Minimum Finding (Dürr-Høyer)',
            'speedup': 'O(√n) vs O(n)',
            'suitability_score': 0.8
        },
        'sorting_algorithm': {
            'quantum_algo': 'Quantum Comparison-Based Sort',
            'speedup': 'Better comparison operations',
            'suitability_score': 0.6
        }
    }
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self):
        return [
            {'name': 'linear_search', 'detector': self._detect_linear_search},
            {'name': 'binary_search', 'detector': self._detect_binary_search},
            {'name': 'brute_force_optimization', 'detector': self._detect_brute_force_opt},
            {'name': 'min_max_problem', 'detector': self._detect_min_max_problem},
            {'name': 'sorting_algorithm', 'detector': self._detect_sorting_algorithm}
        ]
    
    def analyze(self, python_code: str) -> Dict[str, Any]:
        """Main analysis function."""
        try:
            tree = ast.parse(python_code)
            metrics = self._extract_metrics(tree)
            
            # Detect patterns
            detected_patterns = []
            for pattern in self.patterns:
                result = pattern['detector'](tree)
                if result['detected']:
                    pattern_info = {
                        'pattern': pattern['name'],
                        'confidence': result['confidence'],
                        'quantum_mapping': self.QUANTUM_MAPPINGS.get(pattern['name'], {})
                    }
                    detected_patterns.append(pattern_info)
            
            # Calculate suitability
            suitability = self._calculate_suitability(detected_patterns)
            
            return {
                'success': True,
                'metrics': metrics,
                'patterns': detected_patterns,
                'quantum_suitability': suitability
            }
            
        except SyntaxError as e:
            return {
                'success': False,
                'error': f'Syntax error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Analysis error: {str(e)}'
            }
    
    def _extract_metrics(self, tree: ast.AST) -> Dict[str, Any]:
        """Extract basic code metrics."""
        metrics = {
            'has_function': False,
            'has_loop': False,
            'has_condition': False,
            'line_count': len(python_code.split('\n')) if 'python_code' in locals() else 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                metrics['has_function'] = True
            if isinstance(node, (ast.For, ast.While)):
                metrics['has_loop'] = True
            if isinstance(node, ast.If):
                metrics['has_condition'] = True
        
        return metrics
    
    # ===== PATTERN DETECTORS =====
    
    def _detect_linear_search(self, tree: ast.AST) -> Dict[str, Any]:
        """Detect linear search pattern."""
        detected = False
        confidence = 0.0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                has_compare = False
                has_exit = False
                
                for stmt in ast.walk(ast.Module(body=node.body)):
                    if isinstance(stmt, ast.Compare):
                        has_compare = True
                    if isinstance(stmt, (ast.Return, ast.Break)):
                        has_exit = True
                
                if has_compare and has_exit:
                    detected = True
                    confidence = 0.9
                    break
        
        return {'detected': detected, 'confidence': confidence}
    
    def _detect_binary_search(self, tree: ast.AST) -> Dict[str, Any]:
        """Detect binary search."""
        detected = False
        confidence = 0.0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.While):
                # Simple check for binary search structure
                if self._has_mid_calculation(node.body):
                    detected = True
                    confidence = 0.8
                    break
        
        return {'detected': detected, 'confidence': confidence}
    
    def _detect_brute_force_opt(self, tree: ast.AST) -> Dict[str, Any]:
        """Detect brute force optimization."""
        detected = False
        confidence = 0.0
        
        # Count nested loops
        max_nesting = 0
        current_nesting = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            elif isinstance(node, ast.FunctionDef):
                current_nesting = 0
        
        if max_nesting >= 2:
            detected = True
            confidence = min(0.7 + (max_nesting * 0.1), 0.95)
        
        return {'detected': detected, 'confidence': confidence}
    
    def _detect_min_max_problem(self, tree: ast.AST) -> Dict[str, Any]:
        """Detect min/max finding."""
        detected = False
        confidence = 0.0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_minmax_var = False
                has_comparison = False
                
                for stmt in ast.walk(ast.Module(body=node.body)):
                    if isinstance(stmt, ast.Assign):
                        if len(stmt.targets) == 1:
                            if isinstance(stmt.targets[0], ast.Name):
                                var_name = stmt.targets[0].id.lower()
                                if var_name.startswith(('min', 'max')):
                                    has_minmax_var = True
                    
                    if isinstance(stmt, ast.Compare):
                        has_comparison = True
                
                if has_minmax_var and has_comparison:
                    detected = True
                    confidence = 0.85
                    break
        
        return {'detected': detected, 'confidence': confidence}
    
    def _detect_sorting_algorithm(self, tree: ast.AST) -> Dict[str, Any]:
        """Detect sorting algorithm."""
        detected = False
        confidence = 0.0
        
        has_nested_loops = False
        has_swap = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                for inner in ast.walk(node):
                    if isinstance(inner, ast.For):
                        has_nested_loops = True
                    if isinstance(inner, ast.Assign):
                        if isinstance(inner.value, ast.Tuple):
                            has_swap = True
        
        if has_nested_loops and has_swap:
            detected = True
            confidence = 0.8
        
        return {'detected': detected, 'confidence': confidence}
    
    def _has_mid_calculation(self, body: List[ast.AST]) -> bool:
        """Check for mid calculation."""
        for node in ast.walk(ast.Module(body=body)):
            if isinstance(node, ast.Assign):
                if isinstance(node.value, ast.BinOp):
                    if isinstance(node.value.op, ast.FloorDiv):
                        return True
        return False
    
    def _calculate_suitability(self, patterns: List[Dict]) -> Dict[str, Any]:
        """Calculate quantum suitability."""
        if not patterns:
            return {
                'score': 0.0,
                'level': 'low',
                'message': 'No quantum-amenable patterns detected'
            }
        
        # Calculate weighted score
        total_score = 0.0
        for pattern in patterns:
            quantum_info = pattern.get('quantum_mapping', {})
            base_score = quantum_info.get('suitability_score', 0.5)
            confidence = pattern.get('confidence', 0.5)
            total_score += base_score * confidence
        
        avg_score = total_score / len(patterns)
        
        if avg_score >= 0.7:
            level = 'high'
            message = 'Strong candidate for quantum conversion'
        elif avg_score >= 0.4:
            level = 'medium'
            message = 'Moderate quantum advantage potential'
        else:
            level = 'low'
            message = 'Limited quantum advantage expected'
        
        return {
            'score': round(avg_score, 3),
            'level': level,
            'message': message
        }

# Initialize the recognizer
recognizer = QuantumPatternRecognizer()

@app.route('/')
def home():
    """Home endpoint."""
    return jsonify({
        'message': 'AI Code Converter API',
        'version': '1.0',
        'endpoints': {
            '/analyze': 'POST - Analyze Python code for quantum suitability',
            '/patterns': 'GET - List available patterns',
            '/health': 'GET - API health check'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'quantum-pattern-recognizer'
    })

@app.route('/patterns')
def list_patterns():
    """List all detectable patterns."""
    patterns = []
    for pattern_name, info in recognizer.QUANTUM_MAPPINGS.items():
        patterns.append({
            'pattern': pattern_name,
            'quantum_algorithm': info['quantum_algo'],
            'expected_speedup': info['speedup'],
            'base_suitability': info['suitability_score']
        })
    
    return jsonify({
        'patterns': patterns,
        'count': len(patterns)
    })

@app.route('/analyze', methods=['POST'])
def analyze_code():
    """
    Analyze Python code for quantum suitability.
    
    Request format:
    {
        "code": "python code here",
        "include_code": true/false (optional, default: true for high suitability)
    }
    
    Response format:
    {
        "success": true/false,
        "analysis": {
            "patterns": [...],
            "quantum_suitability": {...},
            "metrics": {...}
        },
        "original_code": "code here" (only if suitability is high)
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        code = data.get('code', '')
        
        if not code.strip():
            return jsonify({
                'success': False,
                'error': 'No code provided'
            }), 400
        
        # Perform analysis
        result = recognizer.analyze(code)
        
        if not result['success']:
            return jsonify(result), 400
        
        # Prepare response based on suitability
        suitability = result['quantum_suitability']
        response_data = {
            'success': True,
            'analysis': {
                'patterns': result['patterns'],
                'quantum_suitability': suitability,
                'metrics': result['metrics']
            }
        }
        
        # Add original code only if suitability is high
        if suitability['level'] == 'high':
            response_data['original_code'] = code
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/analyze/batch', methods=['POST'])
def analyze_batch():
    """
    Analyze multiple code snippets in batch.
    
    Request format:
    {
        "codes": [
            {"id": "code1", "code": "python code here"},
            {"id": "code2", "code": "python code here"}
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'codes' not in data:
            return jsonify({
                'success': False,
                'error': 'No codes array provided'
            }), 400
        
        results = []
        for item in data['codes']:
            code_id = item.get('id', f'code_{len(results)}')
            code = item.get('code', '')
            
            if code.strip():
                analysis = recognizer.analyze(code)
                results.append({
                    'id': code_id,
                    'analysis': analysis if analysis['success'] else {'error': analysis.get('error', 'Unknown error')}
                })
            else:
                results.append({
                    'id': code_id,
                    'analysis': {'success': False, 'error': 'Empty code'}
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'total_analyzed': len(results)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Batch analysis error: {str(e)}'
        }), 500

# ===== TEST CLIENT =====
def test_api():
    """Test the API with example requests."""
    import requests
    import json
    
    BASE_URL = "http://localhost:5000"
    
    print("🧪 Testing AI Code Converter API")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1. Health check:")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test 2: List patterns
    print("\n2. Available patterns:")
    response = requests.get(f"{BASE_URL}/patterns")
    patterns = response.json()
    print(f"   Found {patterns['count']} patterns:")
    for p in patterns['patterns']:
        print(f"   • {p['pattern']} -> {p['quantum_algorithm']}")
    
    # Test 3: Analyze code (high suitability)
    print("\n3. Analyzing linear search (high suitability):")
    linear_search = """
def search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1
"""
    
    response = requests.post(
        f"{BASE_URL}/analyze",
        json={"code": linear_search}
    )
    
    result = response.json()
    if result['success']:
        suitability = result['analysis']['quantum_suitability']
        print(f"   Suitability: {suitability['level']} ({suitability['score']})")
        print(f"   Message: {suitability['message']}")
        
        if suitability['level'] == 'high':
            print(f"   Original code included: {'yes' if 'original_code' in result else 'no'}")
        
        if result['analysis']['patterns']:
            print(f"   Detected patterns: {[p['pattern'] for p in result['analysis']['patterns']]}")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    # Test 4: Analyze code (low suitability)
    print("\n4. Analyzing simple function (low suitability):")
    simple_code = """
def add(a, b):
    return a + b
"""
    
    response = requests.post(
        f"{BASE_URL}/analyze",
        json={"code": simple_code}
    )
    
    result = response.json()
    if result['success']:
        suitability = result['analysis']['quantum_suitability']
        print(f"   Suitability: {suitability['level']} ({suitability['score']})")
        print(f"   Message: {suitability['message']}")
        print(f"   Original code included: {'yes' if 'original_code' in result else 'no'}")
    
    print("\n" + "=" * 60)
    print("✅ API Testing Complete!")

if __name__ == '__main__':
    print("🚀 Starting AI Code Converter API Server...")
    print(f"📡 API Endpoints:")
    print(f"   • GET  /           - API documentation")
    print(f"   • GET  /health     - Health check")
    print(f"   • GET  /patterns   - List detectable patterns")
    print(f"   • POST /analyze    - Analyze single code snippet")
    print(f"   • POST /analyze/batch - Analyze multiple snippets")
    print(f"\n🔗 Server running at: http://localhost:5000")
    print(f"📝 Test API with: python {__file__} --test")
    
    # Check if we should run tests
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_api()
    else:
        # Run the Flask app
        app.run(debug=True, host='0.0.0.0', port=5000)