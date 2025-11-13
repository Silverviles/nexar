

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(items, search_val):
    if not items:
        return None
        # Return answer
    '''Search for search_val in array, return index if found'''
    # Return answer
    counter = 0
    while counter < len(items):
        if items[counter] == search_val:
        # Check if match found
            return counter
            # Return answer
    return -1
    # Return answer

# Example usage
values = [2, 5, 8, 12, 16, 23, 38, 45]
answer = linear_search(values, 23)
print(f"Found at index: {answer}")