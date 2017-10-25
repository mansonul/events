from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import Group

from autoslug import AutoSlugField
from ckeditor.fields import RichTextField
from imagekit.models import ProcessedImageField

from .base import (
    form_element_plugin_registry,
    form_handler_plugin_registry,
    get_registered_form_element_plugins,
    get_registered_form_handler_plugins
)

from .exceptions import YouAreNotAllowed
from django.db.models.signals import pre_save
from config.key_generator import create_key


# Create your models here.
class Event(models.Model):
    """The place where an organiser can create an event"""
    title = models.CharField('Event Title', max_length=256)
    slug = AutoSlugField(populate_from='title', default='')
    description = RichTextField(blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now,
                                        auto_now=False,
                                        auto_now_add=False)

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

    location_quota = models.IntegerField(
        default=settings.DEFAULT_EVENT_VALUES['location'])

    collection_quota = models.IntegerField(
        default=settings.DEFAULT_EVENT_VALUES['collection'])

    email_quota = models.IntegerField(
        default=settings.DEFAULT_EVENT_VALUES['email'])

    def __str__(self):
        return str(self.title)

    class Meta:
        unique_together = (
            ('title', 'user'),
            ('title', 'location_quota'),
            ('title', 'collection_quota'),
            ('title', 'email_quota'),
        )


# def event_quota(instance, **kwargs):
#     if instance.__class__.objects.count() < instance.user.event_value:
#         print(instance.user.event_value)
#         raise YouAreNotAllowed('You are not allowed to add more!')


# pre_save.connect(event_quota, sender=Event)


class Location(models.Model):
    event = models.ForeignKey(Event)
    l_title = models.CharField('Location Title',
                               max_length=256,
                               null=True,
                               blank=True)
    slug = AutoSlugField(populate_from='l_title', default='')
    l_date = models.DateTimeField('Date and Time',
                                  default=timezone.now,
                                  auto_now=False,
                                  auto_now_add=False)
    address = models.CharField('Location Address',
                               max_length=255,
                               default='Bucharest')

    def __str__(self):
        return str(self.l_title)


class EmailApp(models.Model):
    event = models.ForeignKey(Event)
    name = models.CharField('Name', max_length=100)
    email = models.EmailField(max_length=70)
    secret = models.CharField(max_length=15, unique=True, blank=True)

    class Meta:
        unique_together = ('event', 'email')

    def __str__(self):
        return str(self.email)

    def save(self, *args, **kwargs):
        if self.secret is None or self.secret == '':
            self.secret = create_key(self)
        super().save(*args, **kwargs)


class AbstractPluginModel(models.Model):
    """Abstract plugin model.

    Used when ``fobi.settings.RESTRICT_PLUGIN_ACCESS`` is set to True.

    :Properties:

        - `plugin_uid` (str): Plugin UID.
        - `users` (django.contrib.auth.models.User): White list of the users
          allowed to use the plugin.
        - `groups` (django.contrib.auth.models.Group): White list of the
          user groups allowed to use the plugin.
    """

    plugin_uid = models.CharField("Plugin UID", max_length=255,
                                  unique=True, editable=False)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                   verbose_name="User",
                                   blank=True)
    groups = models.ManyToManyField(Group, verbose_name="Group", blank=True)

    class Meta(object):
        """Meta class."""
        abstract = True

    def get_registered_plugins(self):
        """Get registered plugins."""
        raise NotImplementedError(
            "You should implement ``get_registered_plugins`` method!"
        )

    def __str__(self):
        return "{0} ({1})".format(
            dict(self.get_registered_plugins()).get(self.plugin_uid, ''),
            self.plugin_uid
        )

    def plugin_uid_code(self):
        """Plugin uid code.

        Mainly used in admin.
        """
        return self.plugin_uid
    plugin_uid_code.allow_tags = True
    plugin_uid_code.short_description = 'UID'

    def plugin_uid_admin(self):
        """Plugin uid admin.

        Mainly used in admin.
        """
        return self.__str__()
    plugin_uid_admin.allow_tags = True
    plugin_uid_admin.short_description = 'Plugin'

    def groups_list(self):
        """Groups list.

        Flat list (comma separated string) of groups allowed to use the
        plugin. Used in Django admin.

        :return string:
        """
        return ', '.join([g.name for g in self.groups.all()])
    groups_list.allow_tags = True
    groups_list.short_description = 'Groups'

    def users_list(self):
        """Users list.

        Flat list (comma separated string) of users allowed to use the
        plugin. Used in Django admin.

        :return string:
        """
        return ', '.join([u.get_username() for u in self.users.all()])
    users_list.allow_tags = True
    users_list.short_description = 'Users'


class FormElement(AbstractPluginModel):
    """Form element.

    Form field plugin. Used when ``fobi.settings.RESTRICT_PLUGIN_ACCESS``
    is set to True.

    :Properties:

        - `plugin_uid` (str): Plugin UID.
        - `users` (django.contrib.auth.models.User): White list of the users
          allowed to use the form element plugin.
        - `groups` (django.contrib.auth.models.Group): White list of the user
          groups allowed to use the form element plugin.
    """
    plugin_uid = models.CharField(
        "Plugin UID", max_length=255, unique=True, editable=False,
        # choices=get_registered_form_element_plugins()
    )
    # objects = FormFieldPluginModelManager()

    class Meta(object):
        """Meta class."""
        abstract = False
        verbose_name = "Form element plugin"
        verbose_name_plural = "Form element plugins"

    def get_registered_plugins(self):
        """Add choices."""
        return get_registered_form_element_plugins()


class FormHandler(AbstractPluginModel):
    """
    Form handler plugin. Used when ``fobi.settings.RESTRICT_PLUGIN_ACCESS``
    is set to True.

    :Properties:

        - `plugin_uid` (str): Plugin UID.
        - `users` (django.contrib.auth.models.User): White list of the users
          allowed to use the form handler plugin.
        - `groups` (django.contrib.auth.models.Group): White list of the
          user groups allowed to use the form handler plugin.
    """
    plugin_uid = models.CharField(
        "Plugin UID",
        max_length=255,
        unique=True,
        editable=False,
        default='db_store'
        # choices=get_registered_form_handler_plugins()
    )
    # objects = FormHandlerPluginModelManager()

    class Meta(object):
        """Class meta."""
        abstract = False
        verbose_name = "Form handler plugin"
        verbose_name_plural = "Form handler plugins"

    def get_registered_plugins(self):
        """Add choices."""
        return get_registered_form_handler_plugins()


class FormEntry(models.Model):
    """Form entry.

    :Properties:

        - `user` (django.contrib.auth.models.User: User owning the plugin.
        - `name` (str): Form name.
        - `title` (str): Form title - used in templates.
        - `slug` (str): Form slug.
        - `description` (str): Form description.
        - `is_public` (bool): If set to True, is visible to public.
        - `position` (int): Ordering position in the wizard.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="User")
    event = models.ForeignKey(Event, default='')
    name = models.CharField("List Title", max_length=255)
    title = models.CharField("Title", max_length=255, null=True,
                             blank=True,)
    slug = AutoSlugField(
        populate_from='name', verbose_name="Slug", unique=True
    )
    is_public = models.BooleanField(
        "Public?", default=False,
        help_text="Makes your form visible to the public.")

    success_page_title = models.CharField(
        "Success page title", max_length=255, null=True, blank=True,
        help_text="Custom message title to display after "
        "valid form is submitted")
    success_page_message = models.TextField(
        "Success page body", null=True, blank=True,
        help_text="Custom message text to display after valid form is "
        "submitted")
    created = models.DateTimeField("Created", null=True, blank=True,
                                   auto_now_add=True)
    updated = models.DateTimeField("Updated", null=True, blank=True,
                                   auto_now=True)

    class Meta(object):
        """Meta class."""

        verbose_name = "Form entry"
        verbose_name_plural = "Form entries"
        unique_together = (('user', 'slug'), ('user', 'name'),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            'fobi.view_form_entry',
            kwargs={'form_entry_slug': self.slug}
        )


class FormFieldsetEntry(models.Model):
    """Form fieldset entry."""

    form_entry = models.ForeignKey(Event, verbose_name="Form",
                                   null=True, blank=True)
    name = models.CharField("Name", max_length=255)
    is_repeatable = models.BooleanField(
        "Is repeatable?", default=False,
        help_text="Makes your form fieldset repeatable.")

    class Meta(object):
        """Meta class."""

        verbose_name = "Form fieldset entry"
        verbose_name_plural = "Form fieldset entries"
        unique_together = (('form_entry', 'name'),)

    def __str__(self):
        return self.name


class BaseAbstractPluginEntry(models.Model):
    """Base for AbstractPluginEntry.

    :Properties:

        - `plugin_data` (str): JSON formatted string with plugin data.
    """

    plugin_data = models.TextField(verbose_name="Plugin data", null=True,
                                   blank=True)

    class Meta(object):
        """Meta class."""
        abstract = True

    def __str__(self):
        return "{0} plugin for user {1}".format(
            self.plugin_uid, self.entry_user
        )

    @property
    def entry_user(self):
        """Get user from the parent container."""

        raise NotImplementedError(
            "You should implement ``entry_user`` property!"
        )

    def get_registered_plugins(self):
        """Get registered plugins."""
        raise NotImplementedError(
            "You should implement ``get_registered_plugins`` method!"
        )

    def get_registry(self):
        """Get registry."""
        raise NotImplementedError(
            "You should implement ``get_registry`` method!"
        )

    def plugin_uid_code(self):
        """Plugin uid code.

        Mainly used in admin.
        """
        return self.plugin_uid

    plugin_uid_code.allow_tags = True
    plugin_uid_code.short_description = 'UID'

    def plugin_name(self):
        """Plugin name."""
        return dict(self.get_registered_plugins()).get(self.plugin_uid, '')

    def get_plugin(self, fetch_related_data=False, request=None):
        """Get plugin.

        Gets the plugin class (by ``plugin_uid`` property), makes an instance
        of it, serves the data stored in ``plugin_data`` field (if available).
        Once all is done, plugin is ready to be rendered.

        :param bool fetch_related_data: When set to True, plugin is told to
            re-fetch all related data (stored in models or other sources).
        :return fobi.base.BasePlugin: Subclass of ``fobi.base.BasePlugin``.
        """
        # Getting form element plugin from registry.
        registry = self.get_registry()
        cls = registry.get(self.plugin_uid)

        if not cls:
            # No need to log here, since already logged in registry.
            if registry.fail_on_missing_plugin:
                err_msg = registry.plugin_not_found_error_message.format(
                    self.plugin_uid, registry.__class__
                )
                raise registry.plugin_not_found_exception_cls(err_msg)
            return None

        # Creating plugin instance.
        plugin = cls(user=self.entry_user)

        # So that plugin has the request object
        plugin.request = request

        return plugin.process(
            self.plugin_data, fetch_related_data=fetch_related_data
        )


class AbstractPluginEntry(BaseAbstractPluginEntry):
    """Abstract plugin entry.

    :Properties:

    - `form_entry` (fobi.models.FormEntry): Form to which the field plugin
      belongs to.
    - `plugin_uid` (str): Plugin UID.
    - `plugin_data` (str): JSON formatted string with plugin data.
    """

    # form_entry = models.ForeignKey(FormEntry, verbose_name="Form")
    form_entry = models.ForeignKey(Event, verbose_name="Form")

    class Meta(object):
        """Meta class."""
        abstract = True

    @property
    def entry_user(self):
        """Get user."""
        return self.form_entry.user


class FormElementEntry(AbstractPluginEntry):
    """Form field entry.

    :Properties:

    - `form` (fobi.models.FormEntry): Form to which the field plugin
      belongs to.
    - `plugin_uid` (str): Plugin UID.
    - `plugin_data` (str): JSON formatted string with plugin data.
    - `form_fieldset_entry`: Fieldset.
    - `position` (int): Entry position.
    """

    plugin_uid = models.CharField(
        "Plugin name", max_length=255,
        # choices=get_registered_form_element_plugins()
    )
    form_fieldset_entry = models.ForeignKey(FormFieldsetEntry,
                                            verbose_name="Form fieldset",
                                            null=True, blank=True)
    position = models.PositiveIntegerField("Position", null=True,
                                           blank=True)

    class Meta(object):
        """Meta class."""
        abstract = False
        verbose_name = "Form element entry"
        verbose_name_plural = "Form element entries"
        ordering = ['position']

    def get_registered_plugins(self):
        """Gets registered plugins."""
        return get_registered_form_element_plugins()

    def get_registry(self):
        """Get registry."""
        return form_element_plugin_registry


# def collection_qouta(instance, **kwargs):
#     print(instance.form_entry.user.collection_value)
#     print(instance.__class__.objects.count())
#     if instance.__class__.objects.count() >= \
#        instance.form_entry.user.collection_value:
#         raise YouAreNotAllowed('You are not allowed to add more!')


# pre_save.connect(collection_qouta, sender=FormElementEntry)


class FormHandlerEntry(AbstractPluginEntry):
    """Form handler entry.

    :Properties:

        - `form_entry` (fobi.models.FormEntry): Form to which the handler
          plugin belongs to.
        - `plugin_uid` (str): Plugin UID.
        - `plugin_data` (str): JSON formatted string with plugin data.
    """

    plugin_uid = models.CharField(
        "Plugin name", max_length=255, default='db_store')

    class Meta(object):
        """Meta class."""

        abstract = False
        verbose_name = "Form handler entry"
        verbose_name_plural = "Form handler entries"

    def get_registered_plugins(self):
        """Gets registered plugins."""
        return get_registered_form_handler_plugins()

    def get_registry(self):
        """Get registry."""
        return form_handler_plugin_registry
