

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(arr: list, target: int) -> int:
    '''Search for target in array, return index if found'''
    # Return result
    for i, val in enumerate(arr):
    if val == target:
    # Check if match found
            return i
            # Return result
    return -1
    # Return result

# Example usage
numbers = [2, 5, 8, 12, 16, 23, 38, 45]
result = linear_search(numbers, 23)
print(f"Found at index: {result}")