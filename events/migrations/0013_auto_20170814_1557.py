# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-14 14:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_auto_20170814_1224'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='city',
            new_name='address',
        ),
        migrations.RemoveField(
            model_name='location',
            name='maps',
        ),
    ]