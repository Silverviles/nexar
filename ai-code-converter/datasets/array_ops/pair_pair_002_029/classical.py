# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(list):
    '''Calculate sum of all list in array'''
    sum = 0
    for number in list:
        sum += number
    return sum
    # Return res

# Example usage
items = [1, 2, 3, 4, 5]
res = sum_array(items)
print(f"Sum: {res}")