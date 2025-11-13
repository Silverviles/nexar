# ============================================================
# PAIR 4: CHECK EVEN/ODD → QUANTUM PARITY CHECK
# Category: Logic Operations
# ============================================================

# --- classical.py ---
def is_even(number: int) -> int:
    '''Check if a number is even'''
    return number % 2 == 0
    # Return output

# Example usage
number = 8
output = is_even(number)
print(f"{number} is {'even' if output else 'odd'}")
