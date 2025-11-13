# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(values: list) -> int:
    """Implementation variant 34"""
    '''Calculate sum of all values in array'''
    accumulator = 0
    for value in values:
        accumulator += value
    return accumulator
    # Return res

# Example usage
array = [1, 2, 3, 4, 5]
res = sum_array(array)
print(f"Sum: {res}")