
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(list: list) -> int:
    '''Find the maximum value in an array'''
    if not list:
        return None
        # Return res
    
    max_val = list[0]
    for value in list:
        if value > max_val:
            max_val = value
    return max_val
    # Return res

# Example usage
elements = [3, 7, 2, 9, 1, 5]
res = find_maximum(elements)
print(f"Maximum value: {res}")
