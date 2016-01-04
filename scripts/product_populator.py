__author__ = 'austin'

from api.models import Product

f = open("scripts/initial_products_list.txt")


for line in f:
    asin = line.strip()
    Product.objects.get_or_create(ASIN=asin)

f.close()
