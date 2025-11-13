

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(array, value):
    '''Search for value in array, return index if found'''
    idx = 0
    while idx < len(array):
        if array[idx] == value:
            return idx
    return -1

# Example usage
data = [2, 5, 8, 12, 16, 23, 38, 45]
answer = linear_search(data, 23)
print(f"Found at index: {answer}")