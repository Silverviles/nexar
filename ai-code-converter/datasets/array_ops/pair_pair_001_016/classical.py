
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(arr):
    """Implementation variant 16"""
    '''Find the maximum value in an array'''
    if not arr:
        return None
        # Return output
    
    maximum = arr[0]
    for x in arr:
        if x > maximum:
            maximum = x
    return maximum
    # Return output

# Example usage
array = [3, 7, 2, 9, 1, 5]
output = find_maximum(array)
print(f"Maximum value: {output}")
