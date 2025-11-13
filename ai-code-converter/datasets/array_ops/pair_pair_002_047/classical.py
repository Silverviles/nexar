# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(values: list) -> int:
    '''Calculate sum of all values in array'''
    sum_val = 0
    for x in values:
        sum_val += x
    return sum_val
    # Return output

# Example usage
array = [1, 2, 3, 4, 5]
output = sum_array(array)
print(f"Sum: {output}")