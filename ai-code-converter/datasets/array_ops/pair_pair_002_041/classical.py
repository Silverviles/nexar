# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(list):
    '''Calculate sum of all list in array'''
    acc = 0
    for val in list:
        acc += val
    return acc

# Example usage
items = [1, 2, 3, 4, 5]
res = sum_array(items)
print(f"Sum: {res}")