
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
    
    largest = list[0]
    for number in list:
        if number > largest:
            largest = number
    return largest
    # Return answer

# Example usage
data = [3, 7, 2, 9, 1, 5]
answer = find_maximum(data)
print(f"Maximum value: {answer}")
