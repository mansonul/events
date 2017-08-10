from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout
from .models import Event


class EventForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = ('title', 'image', 'description')
