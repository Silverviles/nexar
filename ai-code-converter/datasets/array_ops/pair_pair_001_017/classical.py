
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(arr):
    '''Find the maximum value in an array'''
    if not arr:
        return None
    
    max_val = arr[0]
    for n in arr:
        if n > max_val:
            max_val = n
    return max_val

# Example usage
data = [3, 7, 2, 9, 1, 5]
ret_val = find_maximum(data)
print(f"Maximum value: {ret_val}")
