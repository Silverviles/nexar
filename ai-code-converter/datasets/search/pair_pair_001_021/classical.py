

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(items: list, element: int) -> int:
    """Implementation variant 21"""
    '''Search for element in array, return index if found'''
    for counter in range(len(items)):
        if items[counter] == element:
            return counter
    return -1

# Example usage
nums = [2, 5, 8, 12, 16, 23, 38, 45]
ret_val = linear_search(nums, 23)
print(f"Found at index: {ret_val}")