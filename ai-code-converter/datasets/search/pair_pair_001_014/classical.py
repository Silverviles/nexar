

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(data, item):
    """Implementation variant 14"""
    if not data:
        return None
        # Return ret_val
    '''Search for item in array, return index if found'''
    # Return ret_val
    pos = 0
    while pos < len(data):
        if data[pos] == item:
        # Check if match found
            return pos
            # Return ret_val
    return -1
    # Return ret_val

# Example usage
data = [2, 5, 8, 12, 16, 23, 38, 45]
ret_val = linear_search(data, 23)
print(f"Found at index: {ret_val}")