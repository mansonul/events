import datetime

import simplejson as json

from django.utils.translation import ugettext_lazy as _

from .....base import (
    FormHandlerPlugin,
    # FormWizardHandlerPlugin,
    get_form_handler_plugin_widget,
    # get_form_wizard_handler_plugin_widget,
    get_processed_form_data,
    # get_processed_form_wizard_data,
)

from . import UID
from .models import SavedFormDataEntry

from django.urls import reverse

__title__ = 'fobi.contrib.plugins.form_handlers.db_store.base'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2014-2017 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = (
    'DBStoreHandlerPlugin',
)

# *****************************************************************************
# **************************** Form handler ***********************************
# *****************************************************************************

from events.models import EmailApp


class DBStoreHandlerPlugin(FormHandlerPlugin):
    """DB store form handler plugin.

    Can be used only once per form.
    """

    uid = UID
    name = _("DB store")
    allow_multiple = False

    def run(
            self,
            form_entry,
            invitee,
            request,
            form,
            form_element_entries=None):
        """Run.

        :param fobi.models.FormEntry form_entry: Instance of
            ``fobi.models.FormEntry``.
        :param django.http.HttpRequest request:
        :param django.forms.Form form:
        :param iterable form_element_entries: Iterable of
            ``fobi.models.FormElementEntry`` objects.
        """
        # Clean up the values, leave our content fields and empty values.
        field_name_to_label_map, cleaned_data = get_processed_form_data(
            form,
            form_element_entries
        )

        self.save_form_data_entry(
            form_entry,
            invitee,
            request,
            field_name_to_label_map,
            cleaned_data
        )

    def save_form_data_entry(self,
                             form_entry,
                             invitee,
                             request,
                             field_name_to_label_map,
                             cleaned_data):
        """Save form data entry.

        Might be used in integration plugins.
        """
        for key, value in cleaned_data.items():
            if isinstance(value, (datetime.datetime, datetime.date)):
                cleaned_data[key] = value.isoformat() \
                    if hasattr(value, 'isoformat') \
                    else value

        # secrets = EmailApp.objects.filter(secret=secret)
        print('form entry din db: ', field_name_to_label_map)
        # print('invitee din db: ', invitee)
        saved_form_data_entry = SavedFormDataEntry(
            form_entry=form_entry,
            user=request.user if request.user and request.user.pk else None,
            # invitee='self.invitee',
            masa=invitee,
            form_data_headers=json.dumps(field_name_to_label_map),
            saved_data=json.dumps(cleaned_data)
        )
        saved_form_data_entry.save()

    def custom_actions(self, form_entry, request=None):
        """Custom actions.

        Adding a link to view the saved form entries.

        :return iterable:
        """
        widget = get_form_handler_plugin_widget(
            self.uid, request=request, as_instance=True
        )

        if widget:
            view_entries_icon_class = widget.view_entries_icon_class
            export_entries_icon_class = widget.export_entries_icon_class
        else:
            view_entries_icon_class = 'glyphicon glyphicon-list'
            export_entries_icon_class = 'glyphicon glyphicon-export'

        return (
            (
                reverse('events:fobi.contrib.plugins.form_handlers.db_store.'
                        'view_saved_form_data_entries',
                        args=[form_entry.pk]),
                _("View entries"),
                view_entries_icon_class
            ),
            (
                reverse('events:fobi.contrib.plugins.form_handlers.db_store.'
                        'export_saved_form_data_entries',
                        args=[form_entry.pk]),
                _("Export entries"),
                export_entries_icon_class
            ),
        )
