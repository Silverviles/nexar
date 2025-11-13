

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(list: list, item: int) -> int:
    """Implementation variant 38"""
    '''Search for item in array, return index if found'''
    for counter, val in enumerate(list):
    if val == item:
            return counter
    return -1

# Example usage
list = [2, 5, 8, 12, 16, 23, 38, 45]
res = linear_search(list, 23)
print(f"Found at index: {res}")