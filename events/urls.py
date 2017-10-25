from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.EventList.as_view(),
        name='list'
    ),

    # url(
    #     regex=r'^suzi/(?P<pk>\d+)/$',
    #     view=views.CollectionCreateView.as_view(),
    #     name='suzi'
    # ),

    url(
        regex=r'^emails/(?P<pk>\d+)/$',
        view=views.EmailCreate.as_view(),
        name='email-create'
    ),
    url(r'^emails/$', views.upload_csv, name='upload_csv'),
    # url(
    #     regex=r'^emails/export/$',
    #     view=views.export,
    #     name='email-export'
    # ),

    # url(
    #     regex=r'^emails/delete/(?P<pk>\d+)/$',
    #     view=views.EmailDelete.as_view(),
    #     name='email-delete'
    # ),

    url(
        regex=r'^emails/delete/$',
        view=views.delete_post,
        name='email-delete'
    ),

    url(
        regex=r'^create/$',
        view=views.EventCreate.as_view(),
        name='create'
    ),

    url(
        regex=r'^update/(?P<pk>\d+)/$',
        view=views.EventUpdate.as_view(),
        name='update'
    ),

    url(
        regex=r'^delete/(?P<pk>\d+)/$',
        view=views.EventDelete.as_view(),
        name='delete'
    ),

    url(
        regex=r'^location/delete/(?P<pk>\d+)/$',
        view=views.LocationDelete.as_view(),
        name='l-delete'
    ),

    url(
        regex=r'^location/update/(?P<pk>\d+)/$',
        view=views.LocationUpdate.as_view(),
        name='l-update'
    ),

    url(
        regex=r'^(?P<pk>\d+)/$',
        view=views.EventDetail.as_view(),
        name='detail'
    ),

    url(
        regex=r'^(?P<pk>\d+)/location/$',
        view=views.LocationCreate.as_view(),
        name='l-create'
    ),

    # Edit URLs

    # Edit form entry
    url(r'^collections/edit/(?P<form_entry_id>\d+)/$',
        views.edit_form_entry,
        name='fobi.edit_form_entry'),

    # # Edit form entry
    # url(r'^forms/edit/(?P<form_entry_id>\d+)/$',
    #     views.edit_form_entry,
    #     name='fobi.edit_form_entry'),

    # View form entry
    url(r'^view/(?P<form_entry_slug>[\w_\-]+)/$',
        views.view_form_entry,
        name='fobi.view_form_entry'),

    # Forms dashboard
    url(r'^collections/$', view=views.dashboard, name='fobi.dashboard'),

    # Delete form entry
    url(r'^collections/delete/(?P<form_entry_id>\d+)/$',
        views.delete_form_entry,
        name='fobi.delete_form_entry'),

    # Add form element entry
    url(r'^collections/elements/add/(?P<form_entry_id>\d+)/'
        r'(?P<form_element_plugin_uid>[\w_\-]+)/$',
        views.add_form_element_entry,
        name='fobi.add_form_element_entry'),

    # Edit form element entry
    url(r'^collections/elements/edit/(?P<form_element_entry_id>\d+)/$',
        views.edit_form_element_entry,
        name='fobi.edit_form_element_entry'),

    # Delete form element entry
    url(r'^collections/elements/delete/(?P<form_element_entry_id>\d+)/$',
        views.delete_form_element_entry,
        name='fobi.delete_form_element_entry'),

    # ***********************************************************************
    # *********************** Form handler entry CUD ************************
    # ***********************************************************************

    # Add form handler entry
    url(r'^collections/handlers/add/(?P<form_entry_id>\d+)/'
        r'(?P<form_handler_plugin_uid>[\w_\-]+)/$',
        views.add_form_handler_entry,
        name='fobi.add_form_handler_entry'),

    # Edit form handler entry
    url(r'^collections/handlers/edit/(?P<form_handler_entry_id>\d+)/$',
        views.edit_form_handler_entry,
        name='fobi.edit_form_handler_entry'),

    # Delete form handler entry
    url(r'^collections/handlers/delete/(?P<form_handler_entry_id>\d+)/$',
        views.delete_form_handler_entry,
        name='fobi.delete_form_handler_entry'),

    # Form submitted success page
    url(r'^view/submitted/$',
        views.form_entry_submitted,
        name='fobi.form_entry_submitted'),

    # Form submitted success page
    url(r'^view/(?P<form_entry_slug>[\w_\-]+)/submitted/$',
        view=views.form_entry_submitted,
        name='fobi.form_entry_submitted'),

    url(r'^collections/plugins/form-handlers/db-store/',
        include('events.contrib.plugins.form_handlers.db_store.urls')),
]
