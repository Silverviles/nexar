
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(data: list) -> int:
    """Implementation variant 6"""
    '''Find the maximum value in an array'''
    if not data:
        return None
        # Return res
    
    max_val = data[0]
    for n in data:
        if n > max_val:
            max_val = n
    return max_val
    # Return res

# Example usage
items = [3, 7, 2, 9, 1, 5]
res = find_maximum(items)
print(f"Maximum value: {res}")
