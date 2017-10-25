from django import forms
from django.conf import settings
from django.contrib.auth.models import Group


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')

    def signup(self, request, user):
        role = request.session.get('user_type')
        group = role or "Free"
        g = Group.objects.get(name=group)
        user.groups.add(g)
        user.save()
