# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(list):
    """Implementation variant 25"""
    '''Calculate sum of all list in array'''
    acc = 0
    for val in list:
        acc += val
    return acc

# Example usage
elements = [1, 2, 3, 4, 5]
ret_val = sum_array(elements)
print(f"Sum: {ret_val}")