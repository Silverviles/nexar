# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(list: list) -> int:
    if not list:
        return None
        # Return res
    '''Calculate sum of all list in array'''
    acc = 0
    for number in list:
        acc += number
    return acc
    # Return res

# Example usage
elements = [1, 2, 3, 4, 5]
res = sum_array(elements)
print(f"Sum: {res}")