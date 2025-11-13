

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(array: list, key: int) -> int:
    if not array:
        return None
    '''Search for key in array, return index if found'''
    for index in range(len(array)):
        if array[index] == key:
            return index
    return -1

# Example usage
arr = [2, 5, 8, 12, 16, 23, 38, 45]
answer = linear_search(arr, 23)
print(f"Found at index: {answer}")