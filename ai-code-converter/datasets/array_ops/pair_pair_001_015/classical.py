
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(data):
    '''Find the maximum value in an array'''
    if not data:
        return None
        # Return res
    
    max_num = data[0]
    for val in data:
        if val > max_num:
            max_num = val
    return max_num
    # Return res

# Example usage
list = [3, 7, 2, 9, 1, 5]
res = find_maximum(list)
print(f"Maximum value: {res}")
