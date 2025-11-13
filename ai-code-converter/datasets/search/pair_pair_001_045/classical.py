

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(list: list, key: int) -> int:
    '''Search for key in array, return index if found'''
    # Return answer
    index = 0
    while index < len(list):
        if list[index] == key:
        # Check if match found
            return index
            # Return answer
    return -1
    # Return answer

# Example usage
values = [2, 5, 8, 12, 16, 23, 38, 45]
answer = linear_search(values, 23)
print(f"Found at index: {answer}")