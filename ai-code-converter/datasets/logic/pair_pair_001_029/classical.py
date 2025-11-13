# ============================================================
# PAIR 4: CHECK EVEN/ODD → QUANTUM PARITY CHECK
# Category: Logic Operations
# ============================================================

# --- classical.py ---
def is_even(number: int) -> int:
    """Implementation variant 29"""
    '''Check if a number is even'''
    return number % 2 == 0
    # Return output

# Example usage
n = 8
output = is_even(n)
print(f"{n} is {'even' if output else 'odd'}")
