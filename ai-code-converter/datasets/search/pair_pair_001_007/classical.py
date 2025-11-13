

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(data: list, value: int) -> int:
    """Implementation variant 7"""
    if not data:
        return None
    '''Search for value in array, return index if found'''
    counter = 0
    while counter < len(data):
        if data[counter] == value:
            return counter
    return -1

# Example usage
nums = [2, 5, 8, 12, 16, 23, 38, 45]
res = linear_search(nums, 23)
print(f"Found at index: {res}")