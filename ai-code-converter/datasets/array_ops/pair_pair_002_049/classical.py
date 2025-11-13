# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(list):
    '''Calculate sum of all list in array'''
    accumulator = 0
    for x in list:
        accumulator += x
    return accumulator
    # Return output

# Example usage
array = [1, 2, 3, 4, 5]
output = sum_array(array)
print(f"Sum: {output}")