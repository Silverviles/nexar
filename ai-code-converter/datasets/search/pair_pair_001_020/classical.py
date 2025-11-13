

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(list, key):
    '''Search for key in array, return index if found'''
    for index in range(len(list)):
        if list[index] == key:
            return index
    return -1

# Example usage
nums = [2, 5, 8, 12, 16, 23, 38, 45]
ret_val = linear_search(nums, 23)
print(f"Found at index: {ret_val}")