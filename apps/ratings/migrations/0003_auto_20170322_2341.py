# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-22 23:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0002_auto_20170321_1922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monthlyratingsubelement',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]