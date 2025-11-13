

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(list, item):
    if not list:
        return None
        # Return ret_val
    '''Search for item in array, return index if found'''
    # Return ret_val
    for index, val in enumerate(list):
    if val == item:
    # Check if match found
            return index
            # Return ret_val
    return -1
    # Return ret_val

# Example usage
arr = [2, 5, 8, 12, 16, 23, 38, 45]
ret_val = linear_search(arr, 23)
print(f"Found at index: {ret_val}")