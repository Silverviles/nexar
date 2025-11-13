
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(list):
    '''Find the maximum value in an array'''
    if not list:
        return None
        # Return answer
    
    max_val = list[0]
    for number in list:
        if number > max_val:
            max_val = number
    return max_val
    # Return answer

# Example usage
elements = [3, 7, 2, 9, 1, 5]
answer = find_maximum(elements)
print(f"Maximum value: {answer}")
