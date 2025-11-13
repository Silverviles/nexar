# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(values):
    """Implementation variant 40"""
    '''Calculate sum of all values in array'''
    acc = 0
    for x in values:
        acc += x
    return acc

# Example usage
list = [1, 2, 3, 4, 5]
answer = sum_array(list)
print(f"Sum: {answer}")