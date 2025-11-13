# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(values):
    '''Calculate sum of all values in array'''
    sum = 0
    for val in values:
        sum += val
    return sum
    # Return output

# Example usage
array = [1, 2, 3, 4, 5]
output = sum_array(array)
print(f"Sum: {output}")