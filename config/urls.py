from django.utils.translation import ugettext_lazy as _

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
from events.views import (
    # create_form_entry,
    edit_form_entry,
    view_form_entry,
    form_entry_submitted,
    delete_form_entry,
    dashboard,
    add_form_element_entry,
    edit_form_element_entry,
    delete_form_element_entry,
    add_form_handler_entry,
    edit_form_handler_entry,
    delete_form_handler_entry,
    # EventDetailInvitati,
)

urlpatterns = [
    url(r'^$', TemplateView.as_view(
        template_name='pages/home.html'), name='home'),
    # url(r'^about/$', TemplateView.as_view(
    #     template_name='pages/about.html'), name='about'),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),
    url(r'^api-auth/', include(
        'rest_framework.urls',
        namespace='rest_framework')),

    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),

    # User management
    url(r'^users/', include('project.users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),

    # Your stuff: custom urls includes go here
    url(r'^events/', include('events.urls', namespace='events')),

    # API
    url(r'^api/', include('events.api.urls', namespace='api')),

    # url(r'^invitati/(?P<secret>[-\w\d]+)/$',
    #     EventDetailInvitati.as_view(), name='invitati'),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),


    # # View URLs
    # url(r'^fobi/', include('fobi.urls.view')),

    # # # Edit URLs
    # # Create form entry
    # url(r'^forms/create/$',
    #     view=create_form_entry,
    #     name='fobi.create_form_entry'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request,
            kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied,
            kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found,
            kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
