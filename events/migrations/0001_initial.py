# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-04 14:12
from __future__ import unicode_literals

import autoslug.fields
import ckeditor_uploader.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import events.models
import imagekit.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailApp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('email', models.EmailField(max_length=70)),
                ('secret', models.CharField(blank=True, max_length=15, unique=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='spreadsheets')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256, verbose_name='Event Title')),
                ('slug', autoslug.fields.AutoSlugField(default='', editable=False, populate_from='title')),
                ('description', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_public', models.NullBooleanField(default=False)),
                ('invitee', models.CharField(blank=True, max_length=15, unique=True)),
                ('image', imagekit.models.fields.ProcessedImageField(blank=True, null=True, upload_to=events.models.Event.path_and_rename, validators=[events.models.Event.file_size])),
                ('location_quota', models.IntegerField(default=1)),
                ('collection_quota', models.IntegerField(default=3)),
                ('email_quota', models.IntegerField(default=50)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
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
                'verbose_name': 'Form element plugin',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FormElementEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plugin_data', models.TextField(blank=True, null=True, verbose_name='Plugin data')),
                ('plugin_uid', models.CharField(max_length=255, verbose_name='Plugin name')),
                ('position', models.PositiveIntegerField(blank=True, null=True, verbose_name='Position')),
                ('form_entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event', verbose_name='Form')),
            ],
            options={
                'verbose_name_plural': 'Form element entries',
                'verbose_name': 'Form element entry',
                'ordering': ['position'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FormEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='List Title')),
                ('title', models.CharField(blank=True, max_length=255, null=True, verbose_name='Title')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from='name', unique=True, verbose_name='Slug')),
                ('is_public', models.BooleanField(default=False, help_text='Makes your form visible to the public.', verbose_name='Public?')),
                ('success_page_title', models.CharField(blank=True, help_text='Custom message title to display after valid form is submitted', max_length=255, null=True, verbose_name='Success page title')),
                ('success_page_message', models.TextField(blank=True, help_text='Custom message text to display after valid form is submitted', null=True, verbose_name='Success page body')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated')),
                ('event', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='events.Event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name_plural': 'Form entries',
                'verbose_name': 'Form entry',
            },
        ),
        migrations.CreateModel(
            name='FormFieldsetEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('is_repeatable', models.BooleanField(default=False, help_text='Makes your form fieldset repeatable.', verbose_name='Is repeatable?')),
                ('form_entry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='events.Event', verbose_name='Form')),
            ],
            options={
                'verbose_name_plural': 'Form fieldset entries',
                'verbose_name': 'Form fieldset entry',
            },
        ),
        migrations.CreateModel(
            name='FormHandler',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plugin_uid', models.CharField(default='db_store', editable=False, max_length=255, unique=True, verbose_name='Plugin UID')),
                ('groups', models.ManyToManyField(blank=True, to='auth.Group', verbose_name='Group')),
                ('users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name_plural': 'Form handler plugins',
                'verbose_name': 'Form handler plugin',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FormHandlerEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plugin_data', models.TextField(blank=True, null=True, verbose_name='Plugin data')),
                ('plugin_uid', models.CharField(default='db_store', max_length=255, verbose_name='Plugin name')),
                ('form_entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event', verbose_name='Form')),
            ],
            options={
                'verbose_name_plural': 'Form handler entries',
                'verbose_name': 'Form handler entry',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('l_title', models.CharField(blank=True, max_length=256, null=True, verbose_name='Location Title')),
                ('slug', autoslug.fields.AutoSlugField(default='', editable=False, populate_from='l_title')),
                ('l_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date and Time')),
                ('address', models.CharField(default='Bucharest', max_length=255, verbose_name='Location Address')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event')),
            ],
        ),
        migrations.AddField(
            model_name='formelemententry',
            name='form_fieldset_entry',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='events.FormFieldsetEntry', verbose_name='Form fieldset'),
        ),
        migrations.AddField(
            model_name='emailapp',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event'),
        ),
        migrations.AlterUniqueTogether(
            name='formfieldsetentry',
            unique_together=set([('form_entry', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='formentry',
            unique_together=set([('user', 'slug'), ('user', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='event',
            unique_together=set([('title', 'user'), ('title', 'collection_quota'), ('title', 'location_quota'), ('title', 'email_quota')]),
        ),
        migrations.AlterUniqueTogether(
            name='emailapp',
            unique_together=set([('event', 'email')]),
        ),
    ]
