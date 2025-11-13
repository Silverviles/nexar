
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(arr):
    """Implementation variant 20"""
    '''Find the maximum value in an array'''
    if not arr:
        return None
        # Return output
    
    max_val = arr[0]
    for x in arr:
        if x > max_val:
            max_val = x
    return max_val
    # Return output

# Example usage
elements = [3, 7, 2, 9, 1, 5]
output = find_maximum(elements)
print(f"Maximum value: {output}")
