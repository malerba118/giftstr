# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-23 02:39
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='PersonSimilarity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('similarity', models.FloatField()),
                ('person1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ps1', to='api.Person')),
                ('person2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ps2', to='api.Person')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ASIN', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Suggestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relevance', models.FloatField()),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Person')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Product')),
            ],
        ),
        migrations.AddField(
            model_name='person',
            name='likes',
            field=models.ManyToManyField(related_name='liker', to='api.Product'),
        ),
        migrations.AddField(
            model_name='person',
            name='seen',
            field=models.ManyToManyField(related_name='viewer', to='api.Product'),
        ),
        migrations.AddField(
            model_name='person',
            name='suggestions',
            field=models.ManyToManyField(through='api.Suggestion', to='api.Product'),
        ),
        migrations.AddField(
            model_name='person',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
