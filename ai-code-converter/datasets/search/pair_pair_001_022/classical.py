

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(items: list, search_val: int) -> int:
    '''Search for search_val in array, return index if found'''
    # Return answer
    for counter, val in enumerate(items):
    if val == search_val:
    # Check if match found
            return counter
            # Return answer
    return -1
    # Return answer

# Example usage
values = [2, 5, 8, 12, 16, 23, 38, 45]
answer = linear_search(values, 23)
print(f"Found at index: {answer}")