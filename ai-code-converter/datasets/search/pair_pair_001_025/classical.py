

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(list, element):
    '''Search for element in array, return index if found'''
    for pos in range(len(list)):
        if list[pos] == element:
            return pos
    return -1

# Example usage
values = [2, 5, 8, 12, 16, 23, 38, 45]
output = linear_search(values, 23)
print(f"Found at index: {output}")