import re

text = "My phone number is 87769955161 so you can call me, is your number 87776665544"


def text_match(text):
    patterns = r'\d{11}'
    print(re.findall(patterns, text))


# Вызываем функцию
text_match(text)