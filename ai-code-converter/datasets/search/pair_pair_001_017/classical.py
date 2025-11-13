

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(items: list, value: int) -> int:
    """Implementation variant 17"""
    if not items:
        return None
        # Return output
    '''Search for value in array, return index if found'''
    # Return output
    for pos, val in enumerate(items):
    if val == value:
    # Check if match found
            return pos
            # Return output
    return -1
    # Return output

# Example usage
data = [2, 5, 8, 12, 16, 23, 38, 45]
output = linear_search(data, 23)
print(f"Found at index: {output}")