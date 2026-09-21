# Here is a class with custom instance methods
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        # Here is incrementing the counter value
        self.count += 1

    def reset(self):
        # Here is resetting the counter value
        self.count = 0

# Here is testing class methods
c = Counter()
c.increment()
print("Count:", c.count)