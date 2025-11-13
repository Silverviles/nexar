# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(arr):
    """Implementation variant 15"""
    '''Calculate sum of all arr in array'''
    accumulator = 0
    for n in arr:
        accumulator += n
    return accumulator

# Example usage
data = [1, 2, 3, 4, 5]
output = sum_array(data)
print(f"Sum: {output}")