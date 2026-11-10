

with open("shopping.txt", "r") as f:
    items = [item.strip() for item in f]

    for number, item in enumerate(items, start=1):
        print(number, item)


items.append("banana")
items.append("cherry")

items.sort()


with open("shopping_sorted.txt", "x") as f:
    for item in items:
        f.write(item + "\n")

print("\nSorted shopping list:")
for number, item in enumerate(items, start=1):
    print(number, item)
