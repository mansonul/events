from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.EventCreate.as_view(),
        name='create'
    ),

    url(
        regex=r'^created/$',
        view=views.EventList.as_view(),
        name='list'
    ),

    url(
        regex=r'^update/(?P<slug>[-\w]+)/$',
        view=views.EventUpdate.as_view(),
        name='update'
    ),

    url(
        regex=r'^delete/(?P<slug>[-\w]+)/$',
        view=views.EventDelete.as_view(),
        name='delete'
    ),
]
