

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(elements: list, value: int) -> int:
    """Implementation variant 43"""
    '''Search for value in array, return index if found'''
    index = 0
    while index < len(elements):
        if elements[index] == value:
            return index
    return -1

# Example usage
arr = [2, 5, 8, 12, 16, 23, 38, 45]
ret_val = linear_search(arr, 23)
print(f"Found at index: {ret_val}")