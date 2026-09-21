# Here is a function demonstrating positional and default arguments
def calculate_price(price, discount=0.1):
    """Calculates final price after discount."""
    return price * (1 - discount)

# Here is calling function with positional and keyword arguments
print("Default discount:", calculate_price(100))
print("Custom discount:", calculate_price(100, 0.2))