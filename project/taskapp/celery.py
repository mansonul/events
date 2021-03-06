# import os
# from celery import Celery
# from django.apps import apps, AppConfig
# from django.conf import settings


# if not settings.configured:
#     # set the default Django settings module for the 'celery' program.
#     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')  # pragma: no cover


# app = Celery('project')


# class CeleryConfig(AppConfig):
#     name = 'project.taskapp'
#     verbose_name = 'Celery Config'

#     def ready(self):
#         # Using a string here means the worker will not have to
#         # pickle the object when using Windows.
#         app.config_from_object('django.conf:settings')
#         installed_apps = [app_config.name for app_config in apps.get_app_configs()]
#         app.autodiscover_tasks(lambda: installed_apps, force=True)


# @app.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))  # pragma: no cover

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '.config.settings.local')

app = Celery('project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
