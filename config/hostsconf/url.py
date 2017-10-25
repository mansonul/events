from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static

from django.views.generic import TemplateView


from .views import www_root_redirect

# urlpatterns = [
#     # Django Admin, use {% url 'admin:index' %}
#     url(settings.ADMIN_URL, admin.site.urls, name='admin'),
#     url(r'^(?P<path>)', www_root_redirect)
# ]

urlpatterns = [
    # url(r'^events/', include('events.urls', namespace='events')),
    url(r'^about/$', TemplateView.as_view(
        template_name='pages/about.html'), name='about'),
    # url(r'^accounts/', include('allauth.urls'), name='users-all'),
    # url(r'^users/', include('project.users.urls', namespace='users')),
    url(r'^(?P<path>.*)', www_root_redirect),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
