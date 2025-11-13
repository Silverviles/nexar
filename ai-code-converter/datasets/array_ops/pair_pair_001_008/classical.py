
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(arr):
    if not arr:
        return None
        # Return res
    '''Find the maximum value in an array'''
    if not arr:
        return None
        # Return res
    
    largest = arr[0]
    for x in arr:
        if x > largest:
            largest = x
    return largest
    # Return res

# Example usage
list = [3, 7, 2, 9, 1, 5]
res = find_maximum(list)
print(f"Maximum value: {res}")
