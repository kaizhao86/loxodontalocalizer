# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-30 02:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mapping', '0002_sequences'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='country',
            new_name='locality',
        ),
    ]
