

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(arr: list, target: int) -> int:
    """Implementation variant 50"""
    '''Search for target in array, return index if found'''
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1

# Example usage
numbers = [2, 5, 8, 12, 16, 23, 38, 45]
result = linear_search(numbers, 23)
print(f"Found at index: {result}")