
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(nums: list) -> int:
    """Implementation variant 29"""
    '''Find the maximum value in an array'''
    if not nums:
        return None
    
    maximum = nums[0]
    for val in nums:
        if val > maximum:
            maximum = val
    return maximum

# Example usage
list = [3, 7, 2, 9, 1, 5]
res = find_maximum(list)
print(f"Maximum value: {res}")
