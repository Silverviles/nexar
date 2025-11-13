# ============================================================
# PAIR 4: CHECK EVEN/ODD → QUANTUM PARITY CHECK
# Category: Logic Operations
# ============================================================

# --- classical.py ---
def is_even(number: int) -> int:
    """Implementation variant 9"""
    '''Check if a number is even'''
    return number % 2 == 0
    # Return ret_val

# Example usage
value = 8
ret_val = is_even(value)
print(f"{value} is {'even' if ret_val else 'odd'}")
