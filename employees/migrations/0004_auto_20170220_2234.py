# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-20 22:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0003_auto_20170216_1520'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='prefectureemployee',
            options={'ordering': ('last_name',), 'verbose_name': 'Сотрудник префектуры', 'verbose_name_plural': 'Сотрудники префектуры'},
        ),
        migrations.AlterModelOptions(
            name='regionemployee',
            options={'ordering': ('last_name',), 'verbose_name': 'Сотрудник района', 'verbose_name_plural': 'Сотрудники районов'},
        ),
        migrations.RemoveField(
            model_name='prefectureemployee',
            name='district',
        ),
        migrations.RemoveField(
            model_name='regionemployee',
            name='region',
        ),
        migrations.AlterField(
            model_name='prefectureemployee',
            name='can_approve_rating',
            field=models.BooleanField(default=False, verbose_name='Может подтвержать рейтинг'),
        ),
    ]