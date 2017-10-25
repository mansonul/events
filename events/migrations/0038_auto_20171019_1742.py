# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-19 16:42
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0037_auto_20171019_1522'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='collection_quota',
            field=models.IntegerField(default=3),
        ),
        migrations.AddField(
            model_name='event',
            name='email_quota',
            field=models.IntegerField(default=50),
        ),
        migrations.AlterUniqueTogether(
            name='event',
            unique_together=set([('title', 'user'), ('title', 'collection_quota'), ('title', 'email_quota'), ('title', 'location_quota')]),
        ),
    ]
