from django.conf import settings
from django.conf.urls import include, url


urlpatterns = [
    url(r'^accounts/', include('allauth.urls'), name='users-all'),
    # url(r'^events/', include('events.urls', namespace='events')),
    url(r'^users/', include('project.users.urls', namespace='users')),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
