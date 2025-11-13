
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(data):
    """Implementation variant 40"""
    '''Find the maximum value in an array'''
    if not data:
        return None
        # Return ret_val
    
    maximum = data[0]
    for val in data:
        if val > maximum:
            maximum = val
    return maximum
    # Return ret_val

# Example usage
items = [3, 7, 2, 9, 1, 5]
ret_val = find_maximum(items)
print(f"Maximum value: {ret_val}")
