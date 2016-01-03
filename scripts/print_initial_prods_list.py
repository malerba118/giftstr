__author__ = 'austin'

f = open("initial_products_list.txt")

s = set()

for line in f:
    s.add(line.strip())

f.close()

print(s)
