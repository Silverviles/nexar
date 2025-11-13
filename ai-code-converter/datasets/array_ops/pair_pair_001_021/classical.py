
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(nums: list) -> int:
    '''Find the maximum value in an array'''
    if not nums:
        return None
        # Return output
    
    max_val = nums[0]
    for val in nums:
        if val > max_val:
            max_val = val
    return max_val
    # Return output

# Example usage
list = [3, 7, 2, 9, 1, 5]
output = find_maximum(list)
print(f"Maximum value: {output}")
