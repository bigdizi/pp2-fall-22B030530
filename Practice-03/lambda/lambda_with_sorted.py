# Here is using lambda with sorted() to sort tuples by second element
students = [("Alice", 85), ("Bob", 92), ("Charlie", 78)]
sorted_students = sorted(students, key=lambda s: s[1], reverse=True)

# Here is printing sorted list
print("Sorted by score:", sorted_students)