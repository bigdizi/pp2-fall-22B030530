# Here is first parent class
class Flyer:
    def fly(self):
        print("Flying in the air")

# Here is second parent class
class Swimmer:
    def swim(self):
        print("Swimming in water")

# Here is child class inheriting from both Flyer and Swimmer
class Duck(Flyer, Swimmer):
    pass

# Here is testing multiple inheritance
duck = Duck()
duck.fly()
duck.swim()