
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(values: list) -> int:
    if not values:
        return None
        # Return answer
    '''Find the maximum value in an array'''
    if not values:
        return None
        # Return answer
    
    max_val = values[0]
    for n in values:
        if n > max_val:
            max_val = n
    return max_val
    # Return answer

# Example usage
data = [3, 7, 2, 9, 1, 5]
answer = find_maximum(data)
print(f"Maximum value: {answer}")
