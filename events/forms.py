from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from crispy_forms.bootstrap import TabHolder, Tab, Div

from .models import Event, Location, EmailApp

# **************** New ****************** #
import socket

from six.moves.urllib.parse import urlparse

from django import forms
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext, ugettext_lazy as _

from .base import (
    get_registered_form_element_plugins,
    get_registered_form_handler_plugins,
    get_theme,
)
from .constants import ACTION_CHOICES
from .exceptions import ImproperlyConfigured
from .models import (
    # Form plugins
    FormElement,
    FormHandler,

    # Form entries
    FormEntry,
    FormFieldsetEntry,
    FormElementEntry,
    FormHandlerEntry,
)
from .validators import url_exists


class EventForm(ModelForm):

    class Meta:
        model = Event
        fields = (
            'title',
            'image',
            'description',
        )
        widgets = {
            'title': forms.TextInput(
                attrs={'class': 'form-control input-style',
                       'placeholder': 'Please add an Event title*'}),
            'description': forms.Textarea(
                attrs={'placeholder': 'Add a description for your Event'}),
            'image': forms.FileInput(
                attrs={'class': 'file'})}


class LocationForm(ModelForm):

    class Meta:
        model = Location
        fields = (
            'l_title',
            'l_date',
            'address',
        )
        widgets = {
            'l_title': forms.TextInput(
                attrs={'class': 'form-control input-style'}),
            'address': forms.TextInput(
                attrs={'class': 'form-control input-style'}),
            'l_date': forms.TextInput(
                attrs={'class': 'form-control input-style'})
        }


class EmailForm(ModelForm):

    class Meta:
        model = EmailApp
        fields = (
            'name',
            'email',
            'file',
        )
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control input-style'}),
            'email': forms.TextInput(
                attrs={'class': 'form-control input-style'}),
        }


# *****************************************************************************
# *****************************************************************************
# ******************************* Entry forms *********************************
# *****************************************************************************
# *****************************************************************************


class FormEntryDragos(forms.ModelForm):
    class Meta:
        model = FormEntry
        fields = ('name', 'title')


class FormEntryForm(forms.ModelForm):
    """Form for ``fobi.models.FormEntry`` model."""

    class Meta(object):
        """Meta class."""

        # model = FormEntry
        model = Event
        # fields = ('name', 'title')  # 'is_public', 'success_page_title',
        fields = ('title', )  # 'is_public', 'success_page_title',
                  # 'success_page_message','action', 'is_cloneable',

    def __init__(self, *args, **kwargs):
        """Constructor."""
        self.request = kwargs.pop('request', None)
        if self.request is None:
            raise ImproperlyConfigured(
                ugettext(
                    "The {0} form requires a "
                    "request argument.".format(self.__class__.__name__)
                )
            )

        super(FormEntryForm, self).__init__(*args, **kwargs)
        # theme = get_theme(request=None, as_instance=True)

        # self.fields['name'].widget = forms.widgets.TextInput(
        #     attrs={'class': theme.form_element_html_class}
        # )

        # self.fields['name'].widget = forms.widgets.TextInput(
        #     attrs={'class': 'form-control input-style'}
        # )

        # self.fields['title'].widget = forms.widgets.TextInput(
        #     attrs={'class': theme.form_element_html_class}
        # )

        # self.fields['success_page_title'].widget = forms.widgets.TextInput(
        #     attrs={'class': theme.form_element_html_class}
        # )

        # self.fields['success_page_message'].widget = forms.widgets.Textarea(
        #     attrs={'class': theme.form_element_html_class}
        # )

        # At the moment this is done for Foundation 5 theme. Remove this once
        # it's possible for a theme to override this form. Alternatively, add
        # the attrs to the theme API.
        # self.fields['is_public'].widget = forms.widgets.CheckboxInput(
        #     attrs={'data-customforms': 'disabled'}
        # )

    def clean_action(self):
        """Validate the action (URL).

        Checks if URL exists.
        """
        url = self.cleaned_data['action']
        if url:
            full_url = url

            if not (url.startswith('http://') or url.startswith('https://')):
                full_url = self.request.build_absolute_uri(url)

            parsed_url = urlparse(full_url)

            local = False

            try:
                localhost = socket.gethostbyname('localhost')
            except Exception:
                localhost = '127.0.0.1'

            try:
                host = socket.gethostbyname(parsed_url.hostname)

                local = (localhost == host)
            except socket.gaierror:
                pass

            if local:
                full_url = parsed_url.path

            if not url_exists(full_url, local=local):
                raise forms.ValidationError(
                    ugettext("Invalid action URL {0}.").format(full_url)
                )

        return url


class FormFieldsetEntryForm(forms.ModelForm):
    """Form for ``fobi.models.FormFieldsetEntry`` model."""

    class Meta(object):
        """Meta class."""

        model = FormFieldsetEntry
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(FormFieldsetEntryForm, self).__init__(*args, **kwargs)
        theme = get_theme(request=None, as_instance=True)
        self.fields['name'].widget = forms.widgets.TextInput(
            attrs={'class': theme.form_element_html_class}
        )


class FormElementForm(forms.ModelForm):
    """FormElement form."""

    # plugin_uid = forms.ChoiceField(
    #     choices=get_registered_form_element_plugins()
    # )

    class Meta(object):
        """Meta class."""

        model = FormElement
        fields = ('users', 'groups')


class FormElementEntryForm(forms.ModelForm):
    """FormElementEntry form."""

    plugin_uid = forms.ChoiceField(
        choices=get_registered_form_element_plugins()
    )

    class Meta(object):
        """Meta class."""

        model = FormElementEntry
        fields = ('form_entry', 'plugin_data', 'plugin_uid', 'position')


class _FormElementEntryForm(forms.ModelForm):
    """FormElementEntry form.

    To be used with `FormElementEntryFormSet` only.
    """

    class Meta(object):
        """Meta class."""

        model = FormElementEntry
        fields = ('position',)


FormElementEntryFormSet = modelformset_factory(
    FormElementEntry,
    fields=('position',),
    extra=0,
    form=_FormElementEntryForm
)


class FormHandlerForm(forms.ModelForm):
    """FormHandler form."""

    # plugin_uid = forms.ChoiceField(
    #     choices=get_registered_form_handler_plugins()
    # )
    plugin_uid = 'db_store'

    class Meta(object):
        """Meta class."""

        model = FormHandler
        fields = ('users', 'groups')


class FormHandlerEntryForm(forms.ModelForm):
    """FormHandlerEntry form."""

    plugin_uid = forms.ChoiceField(
        choices=get_registered_form_handler_plugins()
    )

    class Meta(object):
        """Meta class."""

        model = FormHandlerEntry
        fields = ('form_entry', 'plugin_data', 'plugin_uid')


# *****************************************************************************
# *****************************************************************************
# *********************************** Base ************************************
# *****************************************************************************
# *****************************************************************************


class BaseBulkChangePluginsForm(forms.ModelForm):
    """Bulk change plugins form.

    - `selected_plugins` (str): List of comma separated values to be
       changed.
    - `users_action` (int): For indicating wheither the users shall be appended
      to the dashbard plugins or replaced.
    - `groups_action` (int): For indicating wheither the groups shall be
      appended to the dashboard plugins or replaced.
    """

    selected_plugins = forms.CharField(
        required=True,
        label=_("Selected plugins"),
        widget=forms.widgets.HiddenInput
    )
    users_action = forms.ChoiceField(
        required=False,
        label=_("Users action"),
        choices=ACTION_CHOICES,
        help_text=_("If set to ``replace``, the groups are replaced; "
                    "otherwise - appended.")
    )
    groups_action = forms.ChoiceField(
        required=False,
        label=_("Groups action"),
        choices=ACTION_CHOICES,
        help_text=_("If set to ``replace``, the groups are replaced; "
                    "otherwise - appended.")
    )

    class Media(object):
        """Media class."""

        css = {
            'all': ('css/admin_custom.css',)
        }

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(BaseBulkChangePluginsForm, self).__init__(*args, **kwargs)
        self.fields['users'].required = False
        self.fields['groups'].required = False


class BulkChangeFormElementPluginsForm(BaseBulkChangePluginsForm):
    """Bulk change form element plugins form."""

    class Meta(object):
        """Meta class."""

        model = FormElement
        fields = ['groups', 'groups_action', 'users', 'users_action']


class BulkChangeFormHandlerPluginsForm(BaseBulkChangePluginsForm):
    """Bulk change form handler plugins form."""

    class Meta(object):
        """Meta class."""

        model = FormHandler
        fields = ['groups', 'groups_action', 'users', 'users_action']
