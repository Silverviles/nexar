# ============================================================
# PAIR 5: SUM OF ARRAY → QUANTUM ACCUMULATOR
# Category: Array Operations
# ============================================================

# --- classical.py ---
def sum_array(data: list) -> int:
    '''Calculate sum of all data in array'''
    acc = 0
    for n in data:
        acc += n
    return acc

# Example usage
elements = [1, 2, 3, 4, 5]
output = sum_array(elements)
print(f"Sum: {output}")