from django.core.urlresolvers import reverse
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DeleteView)
from django.shortcuts import HttpResponseRedirect
from django.http import JsonResponse

from project.users.models import User

from .models import Event
from .forms import EventForm


# Create your views here.
class EventCreate(CreateView):
    """Organiser can create Event in frontend"""
    model = Event
    form_class = EventForm

    def get_template_names(self):
        check_object = Event.objects.filter(
            user=self.request.user
        ).order_by('-title').exists()

        if check_object is False:
            return ['events/event_form.html']

        else:
            return ['events/event_list.html']

    def get_context_data(self, **kwargs):
        context = super(EventCreate, self).get_context_data(**kwargs)
        context['events'] = Event.objects.all()
        return context

    def form_valid(self, form):
        organiser = form.save(commit=False)
        organiser.user = User.objects.get(username=self.request.user)
        organiser.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('events:list')


class EventList(ListView):
    """Organiser can view a list of his events"""
    model = Event

    def get_context_data(self, **kwargs):
        context = super(EventList, self).get_context_data(**kwargs)
        context['events'] = Event.objects.all()
        return context


class EventUpdate(UpdateView):
    """Organiser can update the Event"""
    model = Event
    template_name = 'events/event_form.html'
    form_class = EventForm

    def get_success_url(self):
        return reverse('events:create')


class EventDelete(DeleteView):
    """Organiser can delete the Event"""
    model = Event
    template_name = 'events/event_delete.html'
    form_class = EventForm

    def get_success_url(self):
        return reverse('events:create')