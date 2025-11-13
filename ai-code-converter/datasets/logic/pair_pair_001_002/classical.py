# ============================================================
# PAIR 4: CHECK EVEN/ODD → QUANTUM PARITY CHECK
# Category: Logic Operations
# ============================================================

# --- classical.py ---
def is_even(number):
    '''Check if a number is even'''
    return number % 2 == 0

# Example usage
x = 8
res = is_even(x)
print(f"{x} is {'even' if res else 'odd'}")
