from django.shortcuts import redirect
from django_hosts.resolvers import reverse as host_reverse

from django.shortcuts import get_object_or_404
# from django.contrib.auth.models import User
# from django.conf import settings
from project.users.models import User


def custom_fn(request, username):
    request.viewing_user = get_object_or_404(User, username=username)


def subdomain_callback(request, username=None):
    if not username:
        return redirect(host_reverse("home", host='users'))
    request.subdomain = username
