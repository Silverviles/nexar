
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(arr: list) -> int:
    '''Find the maximum value in an array'''
    if not arr:
        return None
    
    maximum = arr[0]
    for value in arr:
        if value > maximum:
            maximum = value
    return maximum

# Example usage
items = [3, 7, 2, 9, 1, 5]
output = find_maximum(items)
print(f"Maximum value: {output}")
