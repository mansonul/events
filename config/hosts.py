from django.conf import settings
from django_hosts import patterns, host


host_patterns = patterns(
    '',
    host(r'www', settings.ROOT_URLCONF, name='www'),
    # host(r'admin', 'cfehosts.urls.admin', name='admin'),
    # host(r'blog', 'cfehosts.urls.blog', name='blog'),
    host(r'dragos', 'config.hostsconf.urls.users', name='dragos'),
    host(r'(?P<username>\w+)',
         'config.hostsconf.url',
         name='users',
         callback='config.hostsconf.callbacks.subdomain_callback'),
)
