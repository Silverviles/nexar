

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(list, value):
    '''Search for value in array, return index if found'''
    # Return answer
    for pos, val in enumerate(list):
    if val == value:
    # Check if match found
            return pos
            # Return answer
    return -1
    # Return answer

# Example usage
arr = [2, 5, 8, 12, 16, 23, 38, 45]
answer = linear_search(arr, 23)
print(f"Found at index: {answer}")