
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(nums):
    """Implementation variant 24"""
    if not nums:
        return None
    '''Find the maximum value in an array'''
    if not nums:
        return None
    
    max_num = nums[0]
    for x in nums:
        if x > max_num:
            max_num = x
    return max_num

# Example usage
elements = [3, 7, 2, 9, 1, 5]
answer = find_maximum(elements)
print(f"Maximum value: {answer}")
