# ============================================================
# PAIR 4: CHECK EVEN/ODD → QUANTUM PARITY CHECK
# Category: Logic Operations
# ============================================================

# --- classical.py ---
def is_even(number: int) -> int:
    '''Check if a number is even'''
    return number % 2 == 0

# Example usage
num = 8
result = is_even(num)
print(f"{num} is {'even' if result else 'odd'}")
