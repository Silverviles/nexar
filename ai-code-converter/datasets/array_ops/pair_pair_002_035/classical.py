# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(nums):
    """Implementation variant 35"""
    '''Calculate sum of all nums in array'''
    accumulator = 0
    for value in nums:
        accumulator += value
    return accumulator

# Example usage
elements = [1, 2, 3, 4, 5]
output = sum_array(elements)
print(f"Sum: {output}")