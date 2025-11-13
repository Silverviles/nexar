# ============================================================
# PAIR 4: CHECK EVEN/ODD → QUANTUM PARITY CHECK
# Category: Logic Operations
# ============================================================

# --- classical.py ---
def is_even(number: int) -> int:
    """Implementation variant 23"""
    '''Check if a number is even'''
    return number % 2 == 0

# Example usage
val = 8
output = is_even(val)
print(f"{val} is {'even' if output else 'odd'}")
