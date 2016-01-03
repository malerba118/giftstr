__author__ = 'austin'

from api.models import Product

f = open("scripts/asins_better.txt")


for line in f:
    asin = line.strip()
    Product.objects.get_or_create(ASIN=asin)

f.close()
