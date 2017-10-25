from django.http import HttpResponseRedirect
from django_hosts.resolvers import reverse as host_reverse


def www_root_redirect(request, path=None):
    url_ = host_reverse("home", host='www')
    if path is not None:
        url_ = url_ + path
    return HttpResponseRedirect(host_reverse('home'))
