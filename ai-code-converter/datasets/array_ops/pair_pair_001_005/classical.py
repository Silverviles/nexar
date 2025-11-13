
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(data: list) -> int:
    '''Find the maximum value in an array'''
    if not data:
        return None
        # Return output
    
    largest = data[0]
    for number in data:
        if number > largest:
            largest = number
    return largest
    # Return output

# Example usage
data = [3, 7, 2, 9, 1, 5]
output = find_maximum(data)
print(f"Maximum value: {output}")
