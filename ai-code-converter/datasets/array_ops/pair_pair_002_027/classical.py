# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(list: list) -> int:
    """Implementation variant 27"""
    '''Calculate sum of all list in array'''
    acc = 0
    for value in list:
        acc += value
    return acc

# Example usage
list = [1, 2, 3, 4, 5]
output = sum_array(list)
print(f"Sum: {output}")