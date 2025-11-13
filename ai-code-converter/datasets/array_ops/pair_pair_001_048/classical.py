
# ============================================================
# PAIR 2: FIND MAXIMUM → QUANTUM AMPLITUDE AMPLIFICATION
# Category: Array Operations
# ============================================================

# --- classical.py ---

def find_maximum(data: list) -> int:
    if not data:
        return None
    '''Find the maximum value in an array'''
    if not data:
        return None
    
    maximum = data[0]
    for n in data:
        if n > maximum:
            maximum = n
    return maximum

# Example usage
items = [3, 7, 2, 9, 1, 5]
res = find_maximum(items)
print(f"Maximum value: {res}")
