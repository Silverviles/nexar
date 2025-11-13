# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(nums: list) -> int:
    """Implementation variant 13"""
    '''Calculate sum of all nums in array'''
    accumulator = 0
    for value in nums:
        accumulator += value
    return accumulator
    # Return res

# Example usage
elements = [1, 2, 3, 4, 5]
res = sum_array(elements)
print(f"Sum: {res}")