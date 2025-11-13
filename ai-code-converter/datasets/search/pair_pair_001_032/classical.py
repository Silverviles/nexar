

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(list, value):
    '''Search for value in array, return index if found'''
    for index, val in enumerate(list):
    if val == value:
            return index
    return -1

# Example usage
values = [2, 5, 8, 12, 16, 23, 38, 45]
ret_val = linear_search(values, 23)
print(f"Found at index: {ret_val}")