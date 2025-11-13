

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(data, item):
    if not data:
        return None
        # Return answer
    '''Search for item in array, return index if found'''
    # Return answer
    index = 0
    while index < len(data):
        if data[index] == item:
        # Check if match found
            return index
            # Return answer
    return -1
    # Return answer

# Example usage
nums = [2, 5, 8, 12, 16, 23, 38, 45]
answer = linear_search(nums, 23)
print(f"Found at index: {answer}")