
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(nums):
    '''Find the maximum value in an array'''
    if not nums:
        return None
    
    max_num = nums[0]
    for n in nums:
        if n > max_num:
            max_num = n
    return max_num

# Example usage
array = [3, 7, 2, 9, 1, 5]
ret_val = find_maximum(array)
print(f"Maximum value: {ret_val}")
