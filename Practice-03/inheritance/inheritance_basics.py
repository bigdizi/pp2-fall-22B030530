# Here is a parent class Animal
class Animal:
    def speak(self):
        print("Animal makes a sound")

# Here is a child class Dog inheriting from Animal
class Dog(Animal):
    pass

# Here is testing basic inheritance
dog = Dog()
dog.speak()