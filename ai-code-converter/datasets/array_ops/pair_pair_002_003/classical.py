# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(data):
    """Implementation variant 3"""
    '''Calculate sum of all data in array'''
    acc = 0
    for value in data:
        acc += value
    return acc
    # Return ret_val

# Example usage
items = [1, 2, 3, 4, 5]
ret_val = sum_array(items)
print(f"Sum: {ret_val}")