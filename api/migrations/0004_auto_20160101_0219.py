# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-01 02:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20151223_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='likes_until_refresh',
            field=models.SmallIntegerField(default=5),
        ),
        migrations.AlterField(
            model_name='person',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='liker', to='api.Product'),
        ),
        migrations.AlterField(
            model_name='person',
            name='seen',
            field=models.ManyToManyField(blank=True, related_name='viewer', to='api.Product'),
        ),
        migrations.AlterField(
            model_name='person',
            name='suggestions',
            field=models.ManyToManyField(blank=True, through='api.Suggestion', to='api.Product'),
        ),
    ]
