
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(arr: list) -> int:
    '''Find the maximum value in an array'''
    if not arr:
        return None
    
    max_num = arr[0]
    for x in arr:
        if x > max_num:
            max_num = x
    return max_num

# Example usage
items = [3, 7, 2, 9, 1, 5]
answer = find_maximum(items)
print(f"Maximum value: {answer}")
