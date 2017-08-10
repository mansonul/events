from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings

from autoslug import AutoSlugField
from ckeditor.fields import RichTextField
from imagekit.models import ProcessedImageField


# Create your models here.
class Event(models.Model):
    """The place where an organiser can create an event"""
    title = models.CharField(max_length=256)
    slug = AutoSlugField(populate_from='title', default='')
    description = RichTextField(blank=True, null=True)

    def path_and_rename(instance, filename):
        extension = filename.split('.')[-1]
        return '{}.{}'.format(timezone.now(), extension)

    # Application side file size check
    def file_size(value):
        limit = 5 * 1024 * 1024
        if value.size > limit:
            raise ValidationError(
                'File too large. Size should not exceed 5 MB.')

    image = ProcessedImageField(upload_to=path_and_rename,
                                validators=[file_size],
                                format='jpeg',
                                options={'quality': 80},
                                null=True,
                                blank=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)

    def __str__(self):
        return str(self.title)
