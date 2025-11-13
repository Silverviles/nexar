

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(items, search_val):
    """Implementation variant 29"""
    '''Search for search_val in array, return index if found'''
    for index, val in enumerate(items):
    if val == search_val:
            return index
    return -1

# Example usage
data = [2, 5, 8, 12, 16, 23, 38, 45]
answer = linear_search(data, 23)
print(f"Found at index: {answer}")