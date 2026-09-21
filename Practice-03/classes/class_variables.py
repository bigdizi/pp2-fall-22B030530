# Here is demonstrating class variables vs instance variables
class Student:
    university = "KBTU"  # Class variable

    def __init__(self, name):
        self.name = name  # Instance variable

# Here is accessing class and instance variables
s1 = Student("Diaz")
print(f"{s1.name} studies at {Student.university}")