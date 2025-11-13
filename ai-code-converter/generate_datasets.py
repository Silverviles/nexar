"""
Auto-Generate Dataset Variations
Creates meaningful variations from base classical-quantum pairs

Usage:
1. Place base pairs in: base_pairs/category/pair_XXX/classical.py and quantum.py
2. Run: python generate_datasets.py
3. Output: datasets/ folder with all variations
"""

import os
import re
from pathlib import Path
import random
import shutil

# ============================================================
# VARIATION STRATEGIES
# ============================================================

class VariationGenerator:
    
    # Variable name alternatives
    VAR_NAMES = {
        'arr': ['array', 'list', 'items', 'elements', 'data'],
        'target': ['value', 'key', 'item', 'element', 'search_val'],
        'numbers': ['nums', 'values', 'arr', 'data', 'list'],
        'num': ['n', 'value', 'x', 'val', 'number'],
        'i': ['index', 'idx', 'pos', 'counter'],
        'result': ['output', 'res', 'answer', 'ret_val'],
        'total': ['sum', 'accumulator', 'acc', 'sum_val'],
        'max_value': ['maximum', 'max_val', 'largest', 'max_num'],
    }
    
    # Function name alternatives
    FUNC_NAMES = {
        'linear_search': ['find_item', 'search_array', 'locate_value', 'find_element'],
        'find_maximum': ['get_max', 'max_value', 'largest_element', 'find_largest'],
        'add_integers': ['sum_numbers', 'add_nums', 'calculate_sum', 'integer_addition'],
        'is_even': ['check_even', 'even_check', 'is_even_number', 'parity_check'],
        'sum_array': ['array_sum', 'total_sum', 'calculate_total', 'sum_elements'],
    }
    
    # Loop style transformations
    @staticmethod
    def for_to_while(code):
        """Convert for loops to while loops"""
        # Pattern: for i in range(len(arr)):
        pattern = r'for (\w+) in range\(len\((\w+)\)\):'
        
        def replace(match):
            var, arr = match.groups()
            return f'{var} = 0\n    while {var} < len({arr}):'
        
        new_code = re.sub(pattern, replace, code)
        
        # Add increment at end of loop
        if 'while' in new_code:
            lines = new_code.split('\n')
            indented_lines = []
            in_while = False
            indent_level = 0
            
            for line in lines:
                indented_lines.append(line)
                if 'while' in line:
                    in_while = True
                    indent_level = len(line) - len(line.lstrip())
                elif in_while and line.strip() and not line.strip().startswith('#'):
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent <= indent_level:
                        in_while = False
            
            new_code = '\n'.join(indented_lines)
        
        return new_code
    
    @staticmethod
    def add_enumerate(code):
        """Convert range loops to enumerate where appropriate"""
        # Pattern: for i in range(len(arr)): ... arr[i]
        pattern = r'for (\w+) in range\(len\((\w+)\)\):\s+if (\w+)\[(\w+)\]'
        
        def replace(match):
            var, arr, arr2, var2 = match.groups()
            if arr == arr2 and var == var2:
                return f'for {var}, val in enumerate({arr}):\n    if val'
            return match.group(0)
        
        return re.sub(pattern, replace, code)
    
    @staticmethod
    def add_type_hints(code):
        """Add type hints to function"""
        # Pattern: def func_name(param1, param2):
        pattern = r'def (\w+)\(([^)]+)\):'
        
        def replace(match):
            func_name, params = match.groups()
            param_list = [p.strip() for p in params.split(',')]
            
            # Add simple type hints
            typed_params = []
            for param in param_list:
                if 'arr' in param or 'list' in param or 'numbers' in param:
                    typed_params.append(f"{param}: list")
                elif 'target' in param or 'num' in param or 'value' in param:
                    typed_params.append(f"{param}: int")
                else:
                    typed_params.append(param)
            
            return f"def {func_name}({', '.join(typed_params)}) -> int:"
        
        return re.sub(pattern, replace, code)
    
    @staticmethod
    def add_docstring(code, description="Function implementation"):
        """Add docstring to function"""
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                # Insert docstring after function definition
                indent = len(line) - len(line.lstrip())
                docstring = ' ' * (indent + 4) + f'"""{description}"""'
                lines.insert(i + 1, docstring)
                break
        return '\n'.join(lines)
    
    @staticmethod
    def add_edge_cases(code):
        """Add edge case handling"""
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                # Get function parameters
                params = re.search(r'\(([^)]+)\)', line)
                if params:
                    param_list = [p.strip().split(':')[0] for p in params.group(1).split(',')]
                    
                    # Add empty check for array parameters
                    indent = len(lines[i+1]) - len(lines[i+1].lstrip()) if i+1 < len(lines) else 4
                    checks = []
                    for param in param_list:
                        if any(arr_name in param for arr_name in ['arr', 'list', 'numbers', 'array']):
                            checks.append(' ' * indent + f'if not {param}:')
                            checks.append(' ' * indent + '    return None')
                    
                    if checks:
                        lines = lines[:i+1] + checks + lines[i+1:]
                break
        return '\n'.join(lines)
    
    @staticmethod
    def rename_variables(code, var_map):
        """Rename variables throughout code"""
        for old, new in var_map.items():
            # Use word boundaries to avoid partial replacements
            code = re.sub(r'\b' + old + r'\b', new, code)
        return code
    
    @staticmethod
    def add_comments(code):
        """Add descriptive comments"""
        lines = code.split('\n')
        new_lines = []
        
        for line in lines:
            new_lines.append(line)
            
            # Add comments for key operations
            if 'for' in line and 'range' in line:
                indent = len(line) - len(line.lstrip())
                new_lines.append(' ' * indent + '# Iterate through all elements')
            elif 'if' in line and '==' in line:
                indent = len(line) - len(line.lstrip())
                new_lines.append(' ' * indent + '# Check if match found')
            elif 'return' in line:
                indent = len(line) - len(line.lstrip())
                new_lines.append(' ' * indent + '# Return result')
        
        return '\n'.join(new_lines)

# ============================================================
# MAIN GENERATOR
# ============================================================

def generate_variations(base_code, num_variations=10, is_quantum=False):
    """Generate multiple variations of base code"""
    generator = VariationGenerator()
    variations = [base_code]  # Include original
    
    if is_quantum:
        # For quantum code, only do simple variations
        for i in range(num_variations):
            var_code = base_code
            
            # Randomly apply variations
            if random.random() > 0.5:
                var_code = generator.add_comments(var_code)
            
            if random.random() > 0.7:
                var_code = generator.add_type_hints(var_code)
            
            variations.append(var_code)
    else:
        # For classical code, more aggressive variations
        for i in range(num_variations):
            var_code = base_code
            
            # Structural variations (apply 1-2)
            transformations = []
            
            if random.random() > 0.6:
                transformations.append(generator.for_to_while)
            if random.random() > 0.6:
                transformations.append(generator.add_enumerate)
            if random.random() > 0.7:
                transformations.append(generator.add_edge_cases)
            
            # Apply 1-2 structural transformations
            for transform in random.sample(transformations, min(len(transformations), 2)):
                var_code = transform(var_code)
            
            # Syntactic variations (always apply some)
            if random.random() > 0.5:
                var_code = generator.add_type_hints(var_code)
            
            if random.random() > 0.5:
                var_code = generator.add_comments(var_code)
            
            if random.random() > 0.6:
                desc = f"Implementation variant {i+1}"
                var_code = generator.add_docstring(var_code, desc)
            
            # Variable renaming
            if random.random() > 0.4:
                var_map = {}
                for old_var, alternatives in generator.VAR_NAMES.items():
                    if old_var in var_code:
                        var_map[old_var] = random.choice(alternatives)
                
                if var_map:
                    var_code = generator.rename_variables(var_code, var_map)
            
            variations.append(var_code)
    
    return variations

# ============================================================
# FILE OPERATIONS
# ============================================================

def create_dataset_from_base(base_folder="base_pairs", output_folder="datasets", variations_per_pair=10):
    """
    Read base pairs and generate variations
    """
    print("=" * 60)
    print("  DATASET AUTO-GENERATOR")
    print("=" * 60)
    
    base_path = Path(base_folder)
    output_path = Path(output_folder)
    
    if not base_path.exists():
        print(f"❌ Base folder '{base_folder}' not found!")
        print(f"   Create it and add base pairs first.")
        return
    
    # Create output folder
    output_path.mkdir(exist_ok=True)
    
    total_generated = 0
    
    # Walk through base pairs
    for category_folder in base_path.iterdir():
        if not category_folder.is_dir():
            continue
        
        category_name = category_folder.name
        print(f"\n📁 Processing category: {category_name}")
        
        for pair_folder in category_folder.iterdir():
            if not pair_folder.is_dir():
                continue
            
            classical_file = pair_folder / "classical.py"
            quantum_file = pair_folder / "quantum.py"
            
            if not (classical_file.exists() and quantum_file.exists()):
                print(f"   ⚠️  Skipping {pair_folder.name} (missing files)")
                continue
            
            # Read base code
            with open(classical_file, 'r') as f:
                base_classical = f.read()
            with open(quantum_file, 'r') as f:
                base_quantum = f.read()
            
            # Generate variations
            print(f"   🔄 Generating {variations_per_pair} variations for {pair_folder.name}")
            
            classical_vars = generate_variations(base_classical, variations_per_pair, is_quantum=False)
            quantum_vars = generate_variations(base_quantum, variations_per_pair, is_quantum=True)
            
            # Save variations
            for i, (classical, quantum) in enumerate(zip(classical_vars, quantum_vars)):
                var_folder = output_path / category_name / f"pair_{pair_folder.name}_{i:03d}"
                var_folder.mkdir(parents=True, exist_ok=True)
                
                # Save classical
                with open(var_folder / "classical.py", 'w') as f:
                    f.write(classical)
                
                # Save quantum
                with open(var_folder / "quantum.py", 'w') as f:
                    f.write(quantum)
                
                total_generated += 1
            
            print(f"   ✅ Generated {len(classical_vars)} variations")
    
    print(f"\n{'=' * 60}")
    print(f"✅ COMPLETE! Generated {total_generated} total pairs")
    print(f"📂 Output location: {output_folder}/")
    print(f"{'=' * 60}")

# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    # Configuration
    BASE_FOLDER = "base_pairs"
    OUTPUT_FOLDER = "datasets"
    VARIATIONS_PER_PAIR = 50  # Generate 50 variations per base pair
    
    print("\nConfiguration:")
    print(f"  Base folder: {BASE_FOLDER}")
    print(f"  Output folder: {OUTPUT_FOLDER}")
    print(f"  Variations per pair: {VARIATIONS_PER_PAIR}")
    print()
    
    # Generate datasets
    create_dataset_from_base(BASE_FOLDER, OUTPUT_FOLDER, VARIATIONS_PER_PAIR)
    
    print("\n✨ Ready for training!")
    print(f"   Use these datasets with the training script")