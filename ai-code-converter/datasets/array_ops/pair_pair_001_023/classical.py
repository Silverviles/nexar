
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(arr: list) -> int:
    if not arr:
        return None
    '''Find the maximum value in an array'''
    if not arr:
        return None
    
    largest = arr[0]
    for x in arr:
        if x > largest:
            largest = x
    return largest

# Example usage
data = [3, 7, 2, 9, 1, 5]
output = find_maximum(data)
print(f"Maximum value: {output}")
