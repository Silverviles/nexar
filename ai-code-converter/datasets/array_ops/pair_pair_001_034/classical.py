
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(values):
    '''Find the maximum value in an array'''
    if not values:
        return None
    
    maximum = values[0]
    for x in values:
        if x > maximum:
            maximum = x
    return maximum

# Example usage
data = [3, 7, 2, 9, 1, 5]
res = find_maximum(data)
print(f"Maximum value: {res}")
