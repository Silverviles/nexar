
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(data: list) -> int:
    """Implementation variant 35"""
    '''Find the maximum value in an array'''
    if not data:
        return None
    
    maximum = data[0]
    for n in data:
        if n > maximum:
            maximum = n
    return maximum

# Example usage
array = [3, 7, 2, 9, 1, 5]
ret_val = find_maximum(array)
print(f"Maximum value: {ret_val}")
