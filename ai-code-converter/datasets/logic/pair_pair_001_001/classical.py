# ============================================================
# PAIR 4: CHECK EVEN/ODD → QUANTUM PARITY CHECK
# Category: Logic Operations
# ============================================================

# --- classical.py ---
def is_even(number: int) -> int:
    """Implementation variant 1"""
    '''Check if a number is even'''
    return number % 2 == 0

# Example usage
n = 8
ret_val = is_even(n)
print(f"{n} is {'even' if ret_val else 'odd'}")
