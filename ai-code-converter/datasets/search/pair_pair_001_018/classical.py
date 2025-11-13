

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(items, element):
    """Implementation variant 18"""
    if not items:
        return None
        # Return ret_val
    '''Search for element in array, return index if found'''
    # Return ret_val
    for counter in range(len(items)):
    # Iterate through all elements
        if items[counter] == element:
        # Check if match found
            return counter
            # Return ret_val
    return -1
    # Return ret_val

# Example usage
list = [2, 5, 8, 12, 16, 23, 38, 45]
ret_val = linear_search(list, 23)
print(f"Found at index: {ret_val}")