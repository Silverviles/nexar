

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(elements: list, value: int) -> int:
    '''Search for value in array, return index if found'''
    for counter in range(len(elements)):
        if elements[counter] == value:
            return counter
    return -1

# Example usage
data = [2, 5, 8, 12, 16, 23, 38, 45]
output = linear_search(data, 23)
print(f"Found at index: {output}")