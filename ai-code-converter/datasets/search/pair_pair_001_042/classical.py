

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(data: list, key: int) -> int:
    """Implementation variant 42"""
    if not data:
        return None
        # Return ret_val
    '''Search for key in array, return index if found'''
    # Return ret_val
    counter = 0
    while counter < len(data):
        if data[counter] == key:
        # Check if match found
            return counter
            # Return ret_val
    return -1
    # Return ret_val

# Example usage
values = [2, 5, 8, 12, 16, 23, 38, 45]
ret_val = linear_search(values, 23)
print(f"Found at index: {ret_val}")