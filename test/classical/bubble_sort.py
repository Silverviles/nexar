# Pipeline recommendation test fixture -- expected classification: Classical
# Plain O(n^2) in-place bubble sort. No quantum imports or constructs.


def bubble_sort(values):
    n = len(values)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if values[j] > values[j + 1]:
                values[j], values[j + 1] = values[j + 1], values[j]
                swapped = True
        if not swapped:
            break
    return values


if __name__ == "__main__":
    data = [64, 34, 25, 12, 22, 11, 90]
    print(bubble_sort(data))
