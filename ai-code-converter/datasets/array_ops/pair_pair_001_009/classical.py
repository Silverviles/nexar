
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(nums):
    if not nums:
        return None
        # Return res
    '''Find the maximum value in an array'''
    if not nums:
        return None
        # Return res
    
    max_num = nums[0]
    for value in nums:
        if value > max_num:
            max_num = value
    return max_num
    # Return res

# Example usage
items = [3, 7, 2, 9, 1, 5]
res = find_maximum(items)
print(f"Maximum value: {res}")
