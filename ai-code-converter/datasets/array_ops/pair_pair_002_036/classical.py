# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(list):
    """Implementation variant 36"""
    if not list:
        return None
    '''Calculate sum of all list in array'''
    sum = 0
    for n in list:
        sum += n
    return sum

# Example usage
data = [1, 2, 3, 4, 5]
ret_val = sum_array(data)
print(f"Sum: {ret_val}")