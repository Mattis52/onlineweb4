# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-03-30 17:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genfors', '0002_auto_20160309_2133'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='count_blank_votes',
            field=models.BooleanField(default=False, verbose_name='Tellende blanke stemmer'),
        ),
    ]
