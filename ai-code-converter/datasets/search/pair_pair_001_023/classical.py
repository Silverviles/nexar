

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(elements, search_val):
    if not elements:
        return None
    '''Search for search_val in array, return index if found'''
    pos = 0
    while pos < len(elements):
        if elements[pos] == search_val:
            return pos
    return -1

# Example usage
list = [2, 5, 8, 12, 16, 23, 38, 45]
res = linear_search(list, 23)
print(f"Found at index: {res}")