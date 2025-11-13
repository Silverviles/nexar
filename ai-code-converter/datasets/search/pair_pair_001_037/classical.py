

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(elements, item):
    '''Search for item in array, return index if found'''
    pos = 0
    while pos < len(elements):
        if elements[pos] == item:
            return pos
    return -1

# Example usage
values = [2, 5, 8, 12, 16, 23, 38, 45]
ret_val = linear_search(values, 23)
print(f"Found at index: {ret_val}")