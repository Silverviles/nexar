
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(nums: list) -> int:
    if not nums:
        return None
        # Return answer
    '''Find the maximum value in an array'''
    if not nums:
        return None
        # Return answer
    
    maximum = nums[0]
    for x in nums:
        if x > maximum:
            maximum = x
    return maximum
    # Return answer

# Example usage
items = [3, 7, 2, 9, 1, 5]
answer = find_maximum(items)
print(f"Maximum value: {answer}")
