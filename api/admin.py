from django.contrib import admin
import models

# Register your models here.

admin.site.register(models.Product)
admin.site.register(models.Person)
admin.site.register(models.PersonSimilarity)
admin.site.register(models.Suggestion)
admin.site.register(models.Share)