
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(data):
    '''Find the maximum value in an array'''
    if not data:
        return None
        # Return ret_val
    
    max_val = data[0]
    for number in data:
        if number > max_val:
            max_val = number
    return max_val
    # Return ret_val

# Example usage
data = [3, 7, 2, 9, 1, 5]
ret_val = find_maximum(data)
print(f"Maximum value: {ret_val}")
