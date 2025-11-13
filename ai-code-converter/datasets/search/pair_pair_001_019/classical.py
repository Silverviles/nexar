

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(data: list, item: int) -> int:
    """Implementation variant 19"""
    '''Search for item in array, return index if found'''
    for idx, val in enumerate(data):
    if val == item:
            return idx
    return -1

# Example usage
arr = [2, 5, 8, 12, 16, 23, 38, 45]
res = linear_search(arr, 23)
print(f"Found at index: {res}")