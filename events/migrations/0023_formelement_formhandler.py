# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-13 15:21
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0022_formentry_event'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormElement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plugin_uid', models.CharField(editable=False, max_length=255, unique=True, verbose_name='Plugin UID')),
                ('groups', models.ManyToManyField(blank=True, to='auth.Group', verbose_name='Group')),
                ('users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name_plural': 'Form element plugins',
                'abstract': False,
                'verbose_name': 'Form element plugin',
            },
        ),
        migrations.CreateModel(
            name='FormHandler',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plugin_uid', models.CharField(editable=False, max_length=255, unique=True, verbose_name='Plugin UID')),
                ('groups', models.ManyToManyField(blank=True, to='auth.Group', verbose_name='Group')),
                ('users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name_plural': 'Form handler plugins',
                'abstract': False,
                'verbose_name': 'Form handler plugin',
            },
        ),
    ]