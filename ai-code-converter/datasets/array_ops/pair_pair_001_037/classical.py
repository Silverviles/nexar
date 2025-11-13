
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(values):
    '''Find the maximum value in an array'''
    if not values:
        return None
    
    max_num = values[0]
    for n in values:
        if n > max_num:
            max_num = n
    return max_num

# Example usage
elements = [3, 7, 2, 9, 1, 5]
answer = find_maximum(elements)
print(f"Maximum value: {answer}")
