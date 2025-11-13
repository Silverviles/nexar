# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(numbers: list) -> int:
    """Implementation variant 23"""
    if not numbers:
        return None
    '''Calculate sum of all numbers in array'''
    total = 0
    for num in numbers:
        total += num
    return total

# Example usage
arr = [1, 2, 3, 4, 5]
result = sum_array(arr)
print(f"Sum: {result}")