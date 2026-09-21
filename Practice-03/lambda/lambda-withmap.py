# Here is using lambda with map() to convert Celsius to Fahrenheit
celsius_temps = [0, 10, 20, 30]
fahrenheit_temps = list(map(lambda c: (c * 9/5) + 32, celsius_temps))

# Here is printing the mapped results
print("Fahrenheit temperatures:", fahrenheit_temps)