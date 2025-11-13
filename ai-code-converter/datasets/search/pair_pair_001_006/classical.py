

# ============================================================
# PAIR 1: LINEAR SEARCH → GROVER'S SEARCH
# Category: Search
# ============================================================

# --- classical.py ---

def linear_search(data, element):
    '''Search for element in array, return index if found'''
    for idx in range(len(data)):
        if data[idx] == element:
            return idx
    return -1

# Example usage
data = [2, 5, 8, 12, 16, 23, 38, 45]
output = linear_search(data, 23)
print(f"Found at index: {output}")