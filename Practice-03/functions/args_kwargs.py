# Here is a function using *args and **kwargs to accept flexible arguments
def display_info(*args, **kwargs):
    """Displays variable positional and keyword arguments."""
    print("Positional arguments:", args)
    print("Keyword arguments:", kwargs)

# Here is testing *args and **kwargs
display_info(1, 2, 3, course="PP2", topic="Functions")