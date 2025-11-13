
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(list: list) -> int:
    """Implementation variant 2"""
    if not list:
        return None
        # Return res
    '''Find the maximum value in an array'''
    if not list:
        return None
        # Return res
    
    maximum = list[0]
    for n in list:
        if n > maximum:
            maximum = n
    return maximum
    # Return res

# Example usage
elements = [3, 7, 2, 9, 1, 5]
res = find_maximum(elements)
print(f"Maximum value: {res}")
