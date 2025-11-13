# ============================================================
# PAIR 4: CHECK EVEN/ODD → QUANTUM PARITY CHECK
# Category: Logic Operations
# ============================================================

# --- classical.py ---
def is_even(number):
    """Implementation variant 37"""
    '''Check if a number is even'''
    return number % 2 == 0
    # Return res

# Example usage
n = 8
res = is_even(n)
print(f"{n} is {'even' if res else 'odd'}")
