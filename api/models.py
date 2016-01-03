from __future__ import unicode_literals
import random
from datetime import datetime
from urllib2 import HTTPError
from django.contrib.auth.models import User

from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
import math
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from tools.amazon_service import  AmazonService

# Create your models here.


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)



class Product(models.Model):
    ASIN = models.CharField( max_length=100, unique=True)

    def item(self):
        try:
            return AmazonService.productLookup(self.ASIN)
        except KeyError:
            #Purge the system of bad ASINs
            self.delete()
            return {"Error":"Failed to retrieve product"}
        except HTTPError:
            return {"Error":"Failed to retrieve product"}


    def __str__(self):
        return '%s : %s' % (self.id, self.ASIN)



class Person(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=50)
    likes = models.ManyToManyField(Product, blank=True, related_name="liker")
    suggestions = models.ManyToManyField(Product, blank=True, through="Suggestion")
    seen = models.ManyToManyField(Product, blank=True, related_name="viewer")
    permitted = models.ManyToManyField(User, related_name="shared_with_me", through="Share")
    likes_until_refresh = models.SmallIntegerField(default=settings.LIKES_UNTIL_REFRESH)

    class Meta:
        unique_together = ('user', 'name',)

    def __str__(self):
        return '%s' % (self.name)

    def update_person_similarities(self):

        for person in Person.objects.all():

            sim = self._cosine_similarity(person)

            #delete old
            PersonSimilarity.objects.filter(person1=self, person2=person).delete()
            PersonSimilarity.objects.filter(person1=person, person2=self).delete()

            #create new
            PersonSimilarity.objects.create(person1=self, person2=person, similarity=sim)
            if person != self:
                PersonSimilarity.objects.create(person1=person, person2=self, similarity=sim)

    def _cosine_similarity(self, person2):
        intersection = (self.likes.all() & person2.likes.all()).count()
        mag_p1 = math.sqrt(self.likes.count() + 1) #+1 to avoid divide by zero
        mag_p2 = math.sqrt(person2.likes.count() + 1)
        return intersection / (mag_p1 * mag_p2)


    def update_product_suggestions(self):

        #Get most similar people
        ps_set = PersonSimilarity.objects.filter(person1=self).order_by("-similarity")
        ps_set = ps_set[0:settings.NUM_NEAREST_PERSONS]
        most_similar_persons = [ps.person2 for ps in ps_set]

        #Get most relevant products
        #AKA, products liked by most similar persons
        most_similar_products = Product.objects.filter(liker__in=most_similar_persons).distinct()

        #filter to only include products i've not seen
        most_similar_products = most_similar_products.filter(~Q(viewer=self))

        #create new suggestions
        for product in most_similar_products:
            relevance = self._relevance(product, most_similar_persons)
            Suggestion.objects.filter(person=self, product=product).delete()
            Suggestion.objects.create(person=self, product=product, relevance=relevance)

        #create new controlled random suggestions
        random.seed(self._suggestion_seed())
        n = Product.objects.count()
        random_lst = [random.randint(0, n) for i in range(0, settings.NUM_RANDOM_SUGGESTIONS)]
        prods = Product.objects.all()
        for rand_prod in [prods[i] for i in random_lst]:
            if self.has_not_seen(rand_prod):
                Suggestion.objects.filter(person=self, product=rand_prod).delete()
                Suggestion.objects.create(person=self, product=rand_prod, relevance=random.uniform(0,1))

        #create new uncontrolled random suggestionsm
        for rand_prod in Product.objects.all().order_by("?")[0:settings.NUM_RANDOM_SUGGESTIONS]:
            if self.has_not_seen(rand_prod):
                Suggestion.objects.filter(person=self, product=rand_prod).delete()
                Suggestion.objects.create(person=self, product=rand_prod, relevance=random.uniform(0,1))

    def has_not_seen(self, product):
        return Product.objects.filter(Q(pk=product.id) & ~Q(viewer=self)).exists()


    #Seed used to generate random suggestions
    #Necessary to avoid premature convergence/break up clusters
    def _suggestion_seed(self):
        return (datetime.today().second) * datetime.today().month

    def _relevance(self, product, persons):
        numerator = 0
        denominator = 0.01 #to avoid divide by zero
        for p in persons:
            if p.likes.filter(pk=product.id).exists():
                r = 0
            else:
                r = 1
            #possible that another person is in the middle of updating person similarities
            #so PersonSimilarity object may not exist. If so, just ignore it.
            try:
                s = PersonSimilarity.objects.get(person1=self, person2=p).similarity
            except PersonSimilarity.DoesNotExist:
                s = 0
            numerator += r * s
            denominator += s
        return numerator/denominator


class Share(models.Model):
    user = models.ForeignKey(User)
    person = models.ForeignKey(Person)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s can view %s' % (self.user, self.person)

class Suggestion(models.Model):
    person = models.ForeignKey(Person)
    product = models.ForeignKey(Product)
    relevance = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])

    def __str__(self):
        return '%s might like %s' % (self.person, self.product)

class PersonSimilarity(models.Model):
    person1 = models.ForeignKey(Person, related_name="ps1")
    person2 = models.ForeignKey(Person, related_name="ps2")
    similarity = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])

    def __str__(self):
        return '%s is %d percent similar to %s' % (self.person1, self.similarity*100, self.person2)