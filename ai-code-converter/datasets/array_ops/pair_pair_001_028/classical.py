
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(arr: list) -> int:
    '''Find the maximum value in an array'''
    if not arr:
        return None
        # Return answer
    
    max_num = arr[0]
    for value in arr:
        if value > max_num:
            max_num = value
    return max_num
    # Return answer

# Example usage
items = [3, 7, 2, 9, 1, 5]
answer = find_maximum(items)
print(f"Maximum value: {answer}")
