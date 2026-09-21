# Here is parent class Shape
class Shape:
    def area(self):
        return 0

# Here is child class Circle overriding method area
class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14159 * (self.radius ** 2)

# Here is testing method overriding
c = Circle(5)
print("Circle Area:", c.area())