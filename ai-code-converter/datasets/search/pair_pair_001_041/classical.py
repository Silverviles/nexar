

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(list: list, element: int) -> int:
    """Implementation variant 41"""
    if not list:
        return None
    '''Search for element in array, return index if found'''
    for pos in range(len(list)):
        if list[pos] == element:
            return pos
    return -1

# Example usage
data = [2, 5, 8, 12, 16, 23, 38, 45]
ret_val = linear_search(data, 23)
print(f"Found at index: {ret_val}")