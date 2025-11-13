

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(elements: list, key: int) -> int:
    if not elements:
        return None
        # Return res
    '''Search for key in array, return index if found'''
    # Return res
    for idx in range(len(elements)):
    # Iterate through all elements
        if elements[idx] == key:
        # Check if match found
            return idx
            # Return res
    return -1
    # Return res

# Example usage
nums = [2, 5, 8, 12, 16, 23, 38, 45]
res = linear_search(nums, 23)
print(f"Found at index: {res}")