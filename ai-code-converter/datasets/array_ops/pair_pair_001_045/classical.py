
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(values):
    if not values:
        return None
        # Return answer
    '''Find the maximum value in an array'''
    if not values:
        return None
        # Return answer
    
    max_val = values[0]
    for val in values:
        if val > max_val:
            max_val = val
    return max_val
    # Return answer

# Example usage
list = [3, 7, 2, 9, 1, 5]
answer = find_maximum(list)
print(f"Maximum value: {answer}")
