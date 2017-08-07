from django.db import models
from ckeditor.fields import RichTextField


# Create your models here.
class Event(models.Model):
    """The place where a user can create an event"""
    title = models.CharField(max_length=256)
    description = RichTextField(blank=True, null=True)

    def __str__(self):
        return str(self.title)
