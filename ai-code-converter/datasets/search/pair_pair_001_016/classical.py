

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(data, element):
    if not data:
        return None
        # Return answer
    '''Search for element in array, return index if found'''
    # Return answer
    pos = 0
    while pos < len(data):
        if data[pos] == element:
        # Check if match found
            return pos
            # Return answer
    return -1
    # Return answer

# Example usage
values = [2, 5, 8, 12, 16, 23, 38, 45]
answer = linear_search(values, 23)
print(f"Found at index: {answer}")