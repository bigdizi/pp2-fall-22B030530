# Here is a simple class definition for a Book
class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author

# Here is instantiating the Book class
my_book = Book("1984", "George Orwell")
print(f"Book: {my_book.title} by {my_book.author}")