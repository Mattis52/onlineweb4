# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-01-30 19:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0014_auto_20161007_1846'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='old_image',
        ),
    ]