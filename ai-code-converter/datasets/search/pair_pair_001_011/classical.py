

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(data: list, element: int) -> int:
    '''Search for element in array, return index if found'''
    idx = 0
    while idx < len(data):
        if data[idx] == element:
            return idx
    return -1

# Example usage
nums = [2, 5, 8, 12, 16, 23, 38, 45]
ret_val = linear_search(nums, 23)
print(f"Found at index: {ret_val}")