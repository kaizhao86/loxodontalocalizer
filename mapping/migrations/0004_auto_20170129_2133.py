# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-30 02:33
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mapping', '0003_auto_20170129_2132'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='elephant',
            new_name='Elephants',
        ),
        migrations.RenameModel(
            old_name='Haplotype',
            new_name='Haplotypes',
        ),
        migrations.RenameModel(
            old_name='Location',
            new_name='Locations',
        ),
    ]
