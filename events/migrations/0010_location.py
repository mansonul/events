# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-11 12:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_auto_20170808_1507'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
    ]
