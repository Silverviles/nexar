

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(arr: list, target: int) -> int:
    """Implementation variant 36"""
    '''Search for target in array, return index if found'''
    # Return result
    i = 0
    while i < len(arr):
        if arr[i] == target:
        # Check if match found
            return i
            # Return result
    return -1
    # Return result

# Example usage
numbers = [2, 5, 8, 12, 16, 23, 38, 45]
result = linear_search(numbers, 23)
print(f"Found at index: {result}")