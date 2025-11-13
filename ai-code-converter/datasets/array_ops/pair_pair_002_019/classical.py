# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(list: list) -> int:
    '''Calculate sum of all list in array'''
    acc = 0
    for n in list:
        acc += n
    return acc
    # Return ret_val

# Example usage
list = [1, 2, 3, 4, 5]
ret_val = sum_array(list)
print(f"Sum: {ret_val}")