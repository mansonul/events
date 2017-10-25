from __future__ import absolute_import

from events.base import form_element_plugin_registry

from .base import CheckboxSelectMultipleInputPlugin

__title__ = 'events.contrib.plugins.form_elements.fields.' \
            'checkbox_select_multiple.fobi_form_elements'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = '2014-2017 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('CheckboxSelectMultipleInputPlugin',)


form_element_plugin_registry.register(CheckboxSelectMultipleInputPlugin)
