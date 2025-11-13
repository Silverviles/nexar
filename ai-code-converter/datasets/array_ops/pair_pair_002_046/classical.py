# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(nums):
    if not nums:
        return None
    '''Calculate sum of all nums in array'''
    accumulator = 0
    for x in nums:
        accumulator += x
    return accumulator

# Example usage
data = [1, 2, 3, 4, 5]
ret_val = sum_array(data)
print(f"Sum: {ret_val}")