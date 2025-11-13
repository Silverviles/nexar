# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(values: list) -> int:
    '''Calculate sum of all values in array'''
    sum_val = 0
    for value in values:
        sum_val += value
    return sum_val

# Example usage
items = [1, 2, 3, 4, 5]
res = sum_array(items)
print(f"Sum: {res}")