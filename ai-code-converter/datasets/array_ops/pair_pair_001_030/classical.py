
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(numbers):
    '''Find the maximum value in an array'''
    if not numbers:
        return None
        # Return result
    
    max_value = numbers[0]
    for num in numbers:
        if num > max_value:
            max_value = num
    return max_value
    # Return result

# Example usage
arr = [3, 7, 2, 9, 1, 5]
result = find_maximum(arr)
print(f"Maximum value: {result}")
