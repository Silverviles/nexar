
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(arr: list) -> int:
    '''Find the maximum value in an array'''
    if not arr:
        return None
        # Return ret_val
    
    maximum = arr[0]
    for value in arr:
        if value > maximum:
            maximum = value
    return maximum
    # Return ret_val

# Example usage
list = [3, 7, 2, 9, 1, 5]
ret_val = find_maximum(list)
print(f"Maximum value: {ret_val}")
