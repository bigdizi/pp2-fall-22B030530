# Here is parent class Person
class Person:
    def __init__(self, name):
        self.name = name

# Here is child class Student using super()
class Student(Person):
    def __init__(self, name, student_id):
        super().__init__(name)
        self.student_id = student_id

# Here is testing super() call
st = Student("Alice", "22B030530")
print(f"Student: {st.name}, ID: {st.student_id}")