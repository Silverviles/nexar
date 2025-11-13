
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(data: list) -> int:
    if not data:
        return None
        # Return output
    '''Find the maximum value in an array'''
    if not data:
        return None
        # Return output
    
    max_val = data[0]
    for number in data:
        if number > max_val:
            max_val = number
    return max_val
    # Return output

# Example usage
array = [3, 7, 2, 9, 1, 5]
output = find_maximum(array)
print(f"Maximum value: {output}")
