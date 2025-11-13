# ============================================================
# PAIR 4: CHECK EVEN/ODD → QUANTUM PARITY CHECK
# Category: Logic Operations
# ============================================================

# --- classical.py ---
def is_even(number):
    """Implementation variant 10"""
    '''Check if a number is even'''
    return number % 2 == 0

# Example usage
value = 8
answer = is_even(value)
print(f"{value} is {'even' if answer else 'odd'}")
