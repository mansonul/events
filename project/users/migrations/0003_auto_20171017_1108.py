# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-17 10:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_event_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='collection_value',
            field=models.IntegerField(default=3),
        ),
        migrations.AddField(
            model_name='user',
            name='emails_value',
            field=models.IntegerField(default=50),
        ),
        migrations.AddField(
            model_name='user',
            name='location_value',
            field=models.IntegerField(default=1),
        ),
    ]
