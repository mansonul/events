# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-13 09:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0021_auto_20170912_1632'),
    ]

    operations = [
        migrations.AddField(
            model_name='formentry',
            name='event',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='events.Event'),
        ),
    ]
