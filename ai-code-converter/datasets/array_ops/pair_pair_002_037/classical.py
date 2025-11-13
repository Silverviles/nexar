# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(arr: list) -> int:
    '''Calculate sum of all arr in array'''
    sum = 0
    for number in arr:
        sum += number
    return sum
    # Return res

# Example usage
elements = [1, 2, 3, 4, 5]
res = sum_array(elements)
print(f"Sum: {res}")