
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(nums):
    '''Find the maximum value in an array'''
    if not nums:
        return None
        # Return ret_val
    
    max_num = nums[0]
    for value in nums:
        if value > max_num:
            max_num = value
    return max_num
    # Return ret_val

# Example usage
data = [3, 7, 2, 9, 1, 5]
ret_val = find_maximum(data)
print(f"Maximum value: {ret_val}")
