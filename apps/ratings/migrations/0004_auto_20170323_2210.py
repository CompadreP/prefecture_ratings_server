# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-23 22:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0003_auto_20170322_2341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monthlyratingsubelement',
            name='document',
            field=models.FileField(blank=True, null=True, upload_to='uploads/%Y/%m/%d/documents/'),
        ),
    ]