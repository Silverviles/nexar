
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(nums):
    """Implementation variant 36"""
    '''Find the maximum value in an array'''
    if not nums:
        return None
        # Return res
    
    maximum = nums[0]
    for x in nums:
        if x > maximum:
            maximum = x
    return maximum
    # Return res

# Example usage
data = [3, 7, 2, 9, 1, 5]
res = find_maximum(data)
print(f"Maximum value: {res}")
