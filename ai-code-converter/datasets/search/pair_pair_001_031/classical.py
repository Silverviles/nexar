

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(list, search_val):
    '''Search for search_val in array, return index if found'''
    # Return res
    counter = 0
    while counter < len(list):
        if list[counter] == search_val:
        # Check if match found
            return counter
            # Return res
    return -1
    # Return res

# Example usage
list = [2, 5, 8, 12, 16, 23, 38, 45]
res = linear_search(list, 23)
print(f"Found at index: {res}")