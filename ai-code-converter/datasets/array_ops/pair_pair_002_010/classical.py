# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(list: list) -> int:
    """Implementation variant 10"""
    '''Calculate sum of all list in array'''
    sum_val = 0
    for x in list:
        sum_val += x
    return sum_val
    # Return answer

# Example usage
array = [1, 2, 3, 4, 5]
answer = sum_array(array)
print(f"Sum: {answer}")