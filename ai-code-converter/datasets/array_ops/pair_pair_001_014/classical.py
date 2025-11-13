
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(numbers):
    """Implementation variant 14"""
    if not numbers:
        return None
    '''Find the maximum value in an array'''
    if not numbers:
        return None
    
    max_value = numbers[0]
    for num in numbers:
        if num > max_value:
            max_value = num
    return max_value

# Example usage
arr = [3, 7, 2, 9, 1, 5]
result = find_maximum(arr)
print(f"Maximum value: {result}")
