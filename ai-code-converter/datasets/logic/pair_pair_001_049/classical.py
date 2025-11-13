# ============================================================
# PAIR 4: CHECK EVEN/ODD → QUANTUM PARITY CHECK
# Category: Logic Operations
# ============================================================

# --- classical.py ---
def is_even(number):
    """Implementation variant 49"""
    '''Check if a number is even'''
    return number % 2 == 0

# Example usage
number = 8
answer = is_even(number)
print(f"{number} is {'even' if answer else 'odd'}")
