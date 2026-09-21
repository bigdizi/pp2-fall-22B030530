# Here is a function returning multiple values
def get_min_max(numbers):
    """Returns both minimum and maximum values from a list."""
    return min(numbers), max(numbers)

# Here is receiving the returned tuple
low, high = get_min_max([10, 25, 3, 42, 18])
print(f"Min: {low}, Max: {high}")