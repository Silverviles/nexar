# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(values):
    if not values:
        return None
        # Return res
    '''Calculate sum of all values in array'''
    acc = 0
    for value in values:
        acc += value
    return acc
    # Return res

# Example usage
elements = [1, 2, 3, 4, 5]
res = sum_array(elements)
print(f"Sum: {res}")