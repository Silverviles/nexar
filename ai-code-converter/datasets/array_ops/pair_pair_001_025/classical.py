
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(nums):
    if not nums:
        return None
    '''Find the maximum value in an array'''
    if not nums:
        return None
    
    max_val = nums[0]
    for number in nums:
        if number > max_val:
            max_val = number
    return max_val

# Example usage
array = [3, 7, 2, 9, 1, 5]
answer = find_maximum(array)
print(f"Maximum value: {answer}")
