# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(nums):
    '''Calculate sum of all nums in array'''
    accumulator = 0
    for number in nums:
        accumulator += number
    return accumulator

# Example usage
data = [1, 2, 3, 4, 5]
answer = sum_array(data)
print(f"Sum: {answer}")