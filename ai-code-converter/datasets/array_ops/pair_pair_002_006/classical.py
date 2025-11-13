# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(values: list) -> int:
    """Implementation variant 6"""
    '''Calculate sum of all values in array'''
    accumulator = 0
    for n in values:
        accumulator += n
    return accumulator
    # Return output

# Example usage
list = [1, 2, 3, 4, 5]
output = sum_array(list)
print(f"Sum: {output}")