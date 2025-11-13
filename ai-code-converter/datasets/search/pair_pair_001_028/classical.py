

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(data: list, key: int) -> int:
    """Implementation variant 28"""
    '''Search for key in array, return index if found'''
    # Return res
    for pos in range(len(data)):
    # Iterate through all elements
        if data[pos] == key:
        # Check if match found
            return pos
            # Return res
    return -1
    # Return res

# Example usage
values = [2, 5, 8, 12, 16, 23, 38, 45]
res = linear_search(values, 23)
print(f"Found at index: {res}")