# Here is demonstrating constructor initialization
class Car:
    def __init__(self, brand, model, year):
        self.brand = brand
        self.model = model
        self.year = year

# Here is creating a Car instance
car1 = Car("Toyota", "Camry", 2022)
print(f"Car: {car1.year} {car1.brand} {car1.model}")