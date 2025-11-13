

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(items: list, element: int) -> int:
    """Implementation variant 5"""
    if not items:
        return None
        # Return ret_val
    '''Search for element in array, return index if found'''
    # Return ret_val
    for index, val in enumerate(items):
    if val == element:
    # Check if match found
            return index
            # Return ret_val
    return -1
    # Return ret_val

# Example usage
data = [2, 5, 8, 12, 16, 23, 38, 45]
ret_val = linear_search(data, 23)
print(f"Found at index: {ret_val}")