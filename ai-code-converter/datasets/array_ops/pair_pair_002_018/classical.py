# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(nums):
    """Implementation variant 18"""
    '''Calculate sum of all nums in array'''
    acc = 0
    for value in nums:
        acc += value
    return acc

# Example usage
array = [1, 2, 3, 4, 5]
ret_val = sum_array(array)
print(f"Sum: {ret_val}")