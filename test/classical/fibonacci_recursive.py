# Pipeline recommendation test fixture -- expected classification: Classical
# Naive recursive Fibonacci. Deterministic classical control flow only.


def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


if __name__ == "__main__":
    for i in range(10):
        print(fibonacci(i))
