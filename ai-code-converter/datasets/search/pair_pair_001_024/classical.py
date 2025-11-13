

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(data: list, value: int) -> int:
    '''Search for value in array, return index if found'''
    for pos, val in enumerate(data):
    if val == value:
            return pos
    return -1

# Example usage
data = [2, 5, 8, 12, 16, 23, 38, 45]
ret_val = linear_search(data, 23)
print(f"Found at index: {ret_val}")