# --- classical.py ---

def find_first_true(arr):
    for i, v in enumerate(arr):
        if v:
            return i
    return -1
