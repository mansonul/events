from django.db import models


# Create your models here.
class Event(models.Model):
    """The place where a user can create an event"""
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True, null=True)
