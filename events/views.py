import logging
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, QueryDict, HttpResponseRedirect

from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    DeleteView)

from django.shortcuts import get_object_or_404

from project.users.models import User
from .form_importers import get_form_impoter_plugin_urls
from .forms import (
    EventForm,
    EmailForm,
    LocationForm,
    FormEntryForm,
    FormElementEntryFormSet,
)
from .models import (
    Event,
    EmailApp,
    Location,
    FormEntry,
    FormElementEntry,
    FormHandlerEntry)

from django.http import JsonResponse
# ********* New ****************
from django.contrib.auth.decorators import login_required, permission_required
# from .decorators import permissions_required, SATISFY_ALL, SATISFY_ANY
from django.contrib import messages
from django.shortcuts import redirect, render
from django.db import models, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

from .base import (
    fire_form_callbacks,
    run_form_handlers,
    form_element_plugin_registry,
    form_handler_plugin_registry,
    submit_plugin_form_data,
    get_theme,
)
from .constants import (
    CALLBACK_BEFORE_FORM_VALIDATION,
    CALLBACK_FORM_VALID_BEFORE_SUBMIT_PLUGIN_FORM_DATA,
    CALLBACK_FORM_VALID,
    CALLBACK_FORM_VALID_AFTER_FORM_HANDLERS,
    CALLBACK_FORM_INVALID
)
from .dynamic import assemble_form_class
from .settings import GET_PARAM_INITIAL_DATA, DEBUG
from .utils import (
    append_edit_and_delete_links_to_field,
    get_user_form_element_plugins_grouped,
    get_user_form_field_plugin_uids,
    get_user_form_handler_plugins,
    get_user_form_handler_plugin_uids,
)


# class EventList(LoginRequiredMixin, ListView):
class EventList(ListView):
    """Organiser can view a list of his events"""
    model = Event

    def get_context_data(self, **kwargs):
        context = super(EventList, self).get_context_data(**kwargs)
        context['events'] = Event.objects.filter(user=self.request.user)
        # context['events'] = Event.objects.all()
        # context['quota'] = self.request.user.event_value
        return context


class EventDetail(DetailView):
    """Organiser can view a list of his events"""
    model = Event
    template_name = 'events/event_detail.html'

    def get_context_data(self, **kwargs):
        context = super(EventDetail, self).get_context_data(**kwargs)
        context['locations'] = Location.objects.filter(
            event__title=self.object.title)  # .filter(
            # event__user=self.request.user)
        # context['collection'] = FormElementEntry.objects.filter(
        #     form_entry_id=self.object.pk)
        # context['options'] = assemble_form_class(
        #     self.object,
        # )
        # context['collection_quota'] = self.request.user.collection_value
        return context


class EventDelete(LoginRequiredMixin, DeleteView):
    """Organiser can delete the Event"""
    model = Event
    template_name = 'events/event_delete.html'
    form_class = EventForm

    def get_success_url(self):
        return reverse('events:list')


class EventCreate(LoginRequiredMixin, CreateView):
    """Organiser can create Event in frontend"""
    model = Event
    form_class = EventForm

    def get_template_names(self):
        check_object = Event.objects.filter(
            user=self.request.user
        ).order_by('-title').exists()

        check_events_number = Event.objects.filter(
            user=self.request.user).count()

        if check_object is False:
            return ['events/event_form.html']

        elif check_object is True and \
             check_events_number < \
             self.request.user.event_value:
            return ['events/event_form.html']

        else:
            return ['events/event_list.html']

    def get_context_data(self, **kwargs):
        context = super(EventCreate, self).get_context_data(**kwargs)
        context['events'] = Event.objects.filter(user=self.request.user)
        return context

    def form_valid(self, form):
        check_events_number = Event.objects.filter(
            user=self.request.user).count()
        organiser = form.save(commit=False)
        if check_events_number < self.request.user.event_value:
            organiser.user = User.objects.get(username=self.request.user)
            organiser.save()
            return HttpResponseRedirect(
                reverse('events:l-create', args=(organiser.pk,)))
        else:
            return HttpResponseRedirect(
                reverse('events:list'))


class EventUpdate(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('events:list')


class LocationCreate(LoginRequiredMixin, CreateView):
    """Organiser can create Location"""
    template_name = 'events/location_form.html'
    form_class = LocationForm
    model = Location

    def form_valid(self, form):
        # Pass the Foreign Key to the form
        form.instance.event = get_object_or_404(
            Event, pk=self.kwargs.get('pk'))

        # Verify the user quota against default quota
        event_location_quota = Event.objects.filter(
            pk=self.kwargs['pk']).values_list(
            'location_quota', flat=True)[0]
        user_locations_count = Location.objects.filter(
            event__pk=self.kwargs['pk']).filter(
            event__user=self.request.user).count()
        location = form.save(commit=False)

        # Save form only if user passes condition
        if user_locations_count < event_location_quota:
            location.save()
            return super(LocationCreate, self).form_valid(form)

        # Else redirect him to the Events list
        else:
            return HttpResponseRedirect(
                reverse('events:list'))

    # Pass the Event pk to the collection
    def get_success_url(self, **kwargs):
        return reverse_lazy('events:fobi.edit_form_entry',
                            kwargs={'form_entry_id': self.kwargs['pk']})


class LocationDelete(LoginRequiredMixin, DeleteView):
    """Organiser can delete the Location"""
    model = Location
    template_name = 'events/location_delete.html'
    form_class = LocationForm

    # After delete go the event
    def get_success_url(self, **kwargs):
        pk = Location.objects.filter(
            pk=self.kwargs['pk']).values_list(
            'event__pk', flat=True)[0]
        return reverse_lazy('events:detail',
                            kwargs={'pk': pk})


class LocationUpdate(LoginRequiredMixin, UpdateView):
    model = Location
    form_class = LocationForm

    # After update go the event
    def get_success_url(self, **kwargs):
        pk = Location.objects.filter(
            pk=self.kwargs['pk']).values_list('event__pk', flat=True)[0]
        return reverse_lazy('events:detail',
                            kwargs={'pk': pk})


class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """

    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
                'name': self.object.name,
                'email': self.object.email,
            }
            return JsonResponse(data)
        else:
            return response


# from tablib import Dataset


class EmailCreate(LoginRequiredMixin, AjaxableResponseMixin, CreateView):
    """Organiser can create Location"""
    template_name = 'events/email_form.html'
    form_class = EmailForm
    model = EmailApp

    def form_valid(self, form):
        # Pass the Foreign Key to the form
        form.instance.event = get_object_or_404(
            Event, pk=self.kwargs.get('pk'))

        # Verify the user quota against default quota
        event_email_quota = Event.objects.filter(
            pk=self.kwargs['pk']).values_list(
            'email_quota', flat=True)[0]
        user_email_count = EmailApp.objects.filter(
            event__pk=self.kwargs['pk']).filter(
            event__user=self.request.user).count()
        email = form.save(commit=False)

        # Save form only if user passes condition
        if user_email_count < event_email_quota:
            email.save()
            return super().form_valid(form)

        # Else redirect him to the Events list
        else:
            return HttpResponseRedirect(
                reverse('events:list'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['emails'] = EmailApp.objects.filter(
            event__pk=self.kwargs.get('pk')).order_by('-pk')
        context['event_email_quota'] = Event.objects.filter(
            pk=self.kwargs['pk']).values_list(
            'email_quota', flat=True)[0]
        return context

    def get_success_url(self, **kwargs):
        return reverse_lazy('events:list')


# class InviteeURL(DetailView):
#     model = Event
#     template_name = 'invitee_url.html'


import os  # noqa
import csv  # noqa


def upload_csv(request):
    if not request.user.is_authenticated:
        return redirect("home")

    csv_path = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(csv_path) as f:
            reader = csv.reader(f)
            for row in reader:
                event_obj, created = Event.objects.filter(
                    pk=str(row[0]),
                )

                product_obj, created = EmailApp.objects.get_or_create(
                    event=event_obj,
                    name=str(row[1]),
                    email=str(row[2]),
                )

        success = "Added to database"
        context = {"success": success}

    except csv.Error as e:
        print(e)
        context = {'error': e}

    template = "events/email_form.html"

    return render(request, template, context)


# @login_required
def delete_post(request):
    if request.method == 'DELETE':

        post = EmailApp.objects.get(
            pk=int(QueryDict(request.body).get('postpk')))

        post.delete()

        response_data = {}
        response_data['msg'] = 'Post was deleted.'

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )


def _delete_plugin_entry(request,
                         entry_id,
                         entry_model_cls,
                         get_user_plugin_uids_func,
                         message,
                         html_anchor):
    """Abstract delete entry.

    :param django.http.HttpRequest request:
    :param int entry_id:
    :param fobi.models.AbstractPluginEntry entry_model_cls: Subclass of
        ``fobi.models.AbstractPluginEntry``.
    :param callable get_user_plugin_uids_func:
    :param str message:
    :return django.http.HttpResponse:
    """
    try:
        obj = entry_model_cls._default_manager \
                             .select_related('form_entry') \
                             .get(pk=entry_id,
                                  form_entry__user__pk=request.user.pk)
    except ObjectDoesNotExist:
        raise Http404(("{0} not found.").format(
            entry_model_cls._meta.verbose_name)
        )

    form_entry = obj.form_entry
    plugin = obj.get_plugin(request=request)
    plugin.request = request

    plugin._delete_plugin_data()

    obj.delete()

    messages.info(request, message.format(plugin.name))

    redirect_url = reverse(
        'events:fobi.edit_form_entry', kwargs={'form_entry_id': form_entry.pk}
    )
    return redirect("{0}{1}".format(redirect_url, html_anchor))


# *****************************************************************************
# **************************** Add form handler entry *************************
# *****************************************************************************


@login_required
# @permission_required('events.add_formhandlerentry')
def add_form_handler_entry(request,
                           form_entry_id,
                           form_handler_plugin_uid,
                           theme=None,
                           template_name=None):
    """Add form handler entry.

    :param django.http.HttpRequest request:
    :param int form_entry_id:
    :param int form_handler_plugin_uid:
    :param fobi.base.BaseTheme theme: Theme instance.
    :param string template_name:
    :return django.http.HttpResponse:
    """

    print('From handler', form_entry_id)
    try:
        form_entry = Event._default_manager.get(pk=form_entry_id)
    except ObjectDoesNotExist:
        raise Http404("Form entry not found.")

    user_form_handler_plugin_uids = get_user_form_handler_plugin_uids(
        request.user
    )
    print(user_form_handler_plugin_uids)
    if form_handler_plugin_uid not in user_form_handler_plugin_uids:
        raise Http404("Plugin does not exist or you are not allowed "
                      "to use this plugin!")

    form_handler_plugin_cls = form_handler_plugin_registry.get(
        form_handler_plugin_uid
    )

    # Check if we deal with form handler plugin that is only allowed to be
    # used once. In that case, check if it has been used already in the current
    # form entry.
    if not form_handler_plugin_cls.allow_multiple:
        times_used = FormHandlerEntry._default_manager \
            .filter(form_entry__id=form_entry_id,
                    plugin_uid=form_handler_plugin_cls.uid) \
            .count()
        if times_used > 0:
            raise Http404(
                ("The {0} plugin can be used only once in a "
                 "form.").format(form_handler_plugin_cls.name)
            )

    form_handler_plugin = form_handler_plugin_cls(user=request.user)
    form_handler_plugin.request = request

    form_handler_plugin_form_cls = form_handler_plugin.get_form()
    form = None

    obj = FormHandlerEntry()
    obj.form_entry = form_entry
    obj.plugin_uid = form_handler_plugin_uid
    obj.user = request.user

    save_object = False

    if not form_handler_plugin_form_cls:
        save_object = True

    elif request.method == 'POST':
        form = form_handler_plugin.get_initialised_create_form_or_404(
            data=request.POST,
            files=request.FILES
        )
        if form.is_valid():
            # Saving the plugin form data.
            form.save_plugin_data(request=request)

            # Getting the plugin data.
            obj.plugin_data = form.get_plugin_data(request=request)

            save_object = True

    else:
        form = form_handler_plugin.get_initialised_create_form_or_404()

    if save_object:
        # Save the object.
        obj.save()

        messages.info(
            request,
            ('The form handler plugin "{0}" was added '
             'successfully.').format(form_handler_plugin.name)
        )
        # return redirect(
        #     "{0}?active_tab=tab-form-handlers".format(
        #         reverse(
        #             'fobi.edit_form_entry',
        #             kwargs={'form_entry_id': form_entry_id}
        #         )
        #     )
        # )
        return redirect(reverse('events:list'))

    context = {
        'form': form,
        'form_entry': form_entry,
        'form_handler_plugin': form_handler_plugin,
    }
    # If given, pass to the template (and override the value set by
    # the context processor.
    if theme:
        context.update({'fobi_theme': theme})

    if not template_name:
        if not theme:
            theme = get_theme(request=request, as_instance=True)
        template_name = theme.add_form_handler_entry_template

    return render(request, template_name, context)


# *****************************************************************************
# **************************** Edit form handler entry ************************
# *****************************************************************************


# @login_required
# @permission_required('events.change_formhandlerentry')
def edit_form_handler_entry(request,
                            form_handler_entry_id,
                            theme=None,
                            template_name=None):
    """Edit form handler entry.

    :param django.http.HttpRequest request:
    :param int form_handler_entry_id:
    :param fobi.base.BaseTheme theme: Theme instance.
    :param string template_name:
    :return django.http.HttpResponse:
    """
    try:
        obj = FormHandlerEntry._default_manager \
                              .select_related('form_entry') \
                              .get(pk=form_handler_entry_id)
    except ObjectDoesNotExist:
        raise Http404("Form handler entry not found.")

    form_entry = obj.form_entry

    form_handler_plugin = obj.get_plugin(request=request)
    form_handler_plugin.request = request

    FormHandlerPluginForm = form_handler_plugin.get_form()
    form = None

    if not FormHandlerPluginForm:
        messages.info(
            request,
            ('The form handler plugin "{0}" is not '
             'configurable!').format(form_handler_plugin.name)
        )
        return redirect('events:fobi.edit_form_entry',
                        form_entry_id=form_entry.pk)

    elif request.method == 'POST':
        form = form_handler_plugin.get_initialised_edit_form_or_404(
            data=request.POST,
            files=request.FILES
        )

        if form.is_valid():
            # Saving the plugin form data.
            form.save_plugin_data(request=request)

            # Getting the plugin data.
            obj.plugin_data = form.get_plugin_data(request=request)

            # Save the object.
            obj.save()

            messages.info(
                request,
                ('The form handler plugin "{0}" was edited '
                 'successfully.').format(form_handler_plugin.name)
            )

            return redirect('events:fobi.edit_form_entry',
                            form_entry_id=form_entry.pk)

    else:
        form = form_handler_plugin.get_initialised_edit_form_or_404()

    context = {
        'form': form,
        'form_entry': form_entry,
        'form_handler_plugin': form_handler_plugin,
    }

    # If given, pass to the template (and override the value set by
    # the context processor.
    if theme:
        context.update({'fobi_theme': theme})

    if not template_name:
        if not theme:
            theme = get_theme(request=request, as_instance=True)
        template_name = theme.edit_form_handler_entry_template

    return render(request, template_name, context)


# *****************************************************************************
# **************************** Delete form handler entry **********************
# *****************************************************************************


# @login_required
# @permission_required('events.delete_formhandlerentry')
def delete_form_handler_entry(request, form_handler_entry_id):
    """Delete form handler entry.

    :param django.http.HttpRequest request:
    :param int form_handler_entry_id:
    :return django.http.HttpResponse:
    """
    return _delete_plugin_entry(
        request=request,
        entry_id=form_handler_entry_id,
        entry_model_cls=FormHandlerEntry,
        get_user_plugin_uids_func=get_user_form_handler_plugin_uids,
        message='The form handler plugin "{0}" '
                'was deleted successfully.',
        html_anchor='?active_tab=tab-form-handlers'
    )


# *****************************************************************************
# **************************** Create form entry ******************************
# *****************************************************************************

@login_required
def edit_form_entry(request, form_entry_id, theme=None, template_name=None):
    """Edit form entry.

    :param django.http.HttpRequest request:
    :param int form_entry_id:
    :param fobi.base.BaseTheme theme: Theme instance.
    :param str template_name:
    :return django.http.HttpResponse:
    """
    try:
        form_entry = Event._default_manager \
                          .select_related('user') \
                          .prefetch_related('formelemententry_set') \
                          .get(pk=form_entry_id, user__pk=request.user.pk)

    except ObjectDoesNotExist as err:
        raise Http404("Form entry not found.")

    if request.method == 'POST':
        # The form entry form (does not contain form elements)
        form = FormEntryForm(request.POST, request.FILES, instance=form_entry,
                             request=request)

        # This is where we save ordering if it has been changed.
        # The `FormElementEntryFormSet` contain ids and positions only.
        if 'ordering' in request.POST:
            form_element_entry_formset = FormElementEntryFormSet(
                request.POST,
                request.FILES,
                queryset=form_entry.formelemententry_set.all(),
                # prefix = 'form_element'
            )
            # If form elements aren't properly made (developers's fault)
            # there might be problems with saving the ordering - likely
            # in case of hidden elements only. Thus, we want to avoid
            # errors here.
            try:
                if form_element_entry_formset.is_valid():
                    form_element_entry_formset.save()
                    messages.info(
                        request,
                        "Elements ordering edited successfully."
                    )
                    return redirect(
                        reverse('events:fobi.edit_form_entry',
                                kwargs={'form_entry_id': form_entry_id})
                    )
            except MultiValueDictKeyError as err:  # noqa
                messages.error(
                    request,
                    "Errors occurred while trying to change the "
                    "elements ordering!")
                return redirect(
                    reverse('events:fobi.edit_form_entry',
                            kwargs={'form_entry_id': form_entry_id})
                )
        else:
            form_element_entry_formset = FormElementEntryFormSet(
                queryset=form_entry.formelemententry_set.all(),
                # prefix='form_element'
            )

        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            try:
                obj.save()
                messages.info(
                    request,
                    ('Form {0} was edited successfully.').format(
                        form_entry.name
                    )
                )
                return redirect(
                    reverse(
                        'events:fobi.edit_form_entry',
                        kwargs={'form_entry_id': form_entry_id}
                    )
                )
            except IntegrityError as err:
                messages.info(
                    request,
                    (
                        'Errors occurred while saving the form: {0}.'
                    ).format(str(err))
                )
    else:
        # The form entry form (does not contain form elements)
        form = FormEntryForm(instance=form_entry, request=request)

        form_element_entry_formset = FormElementEntryFormSet(
            queryset=form_entry.formelemententry_set.all(),
            # prefix='form_element'
        )

    # In case of success, we don't need this (since redirect would happen).
    # Thus, fetch only if needed.
    form_elements = form_entry.formelemententry_set.all()
    form_handlers = form_entry.formhandlerentry_set.all()[:]
    used_form_handler_uids = [form_handler.plugin_uid
                              for form_handler
                              in form_handlers]

    # The code below (two lines below) is not really used at the moment,
    # thus - comment out, but do not remove, as we might need it later on.
    # all_form_entries = FormEntry._default_manager \
    #                            .only('id', 'name', 'slug') \
    #                            .filter(user__pk=request.user.pk)

    # List of form element plugins allowed to user
    user_form_element_plugins = get_user_form_element_plugins_grouped(
        request.user
    )
    # List of form handler plugins allowed to user
    user_form_handler_plugins = get_user_form_handler_plugins(
        request.user,
        exclude_used_singles=True,
        used_form_handler_plugin_uids=used_form_handler_uids
    )

    # Assembling the form for preview
    form_cls = assemble_form_class(
        form_entry,
        origin='edit_form_entry',
        origin_kwargs_update_func=append_edit_and_delete_links_to_field,
        request=request
    )

    assembled_form = form_cls()
    # print('assembled_form', assembled_form)

    # In debug mode, try to identify possible problems.
    if DEBUG:
        assembled_form.as_p()
    else:
        try:
            assembled_form.as_p()
        except Exception as err:
            logger.error(err)

    # If no theme provided, pick a default one.
    if not theme:
        theme = get_theme(request=request, as_instance=True)

    theme.collect_plugin_media(form_elements)

    # Verify the user quota against default quota
    event_location_quota = Event.objects.filter(
        pk=form_entry.pk).values_list(
        'collection_quota', flat=True)[0]
    user_locations_count = FormEntry.objects.filter(
        event__pk=form_entry.pk).filter(
        event__user=request.user).count()

    context = {
        'form': form,
        'form_entry': form_entry,
        'form_elements': form_elements,
        'form_handlers': form_handlers,
        # 'all_form_entries': all_form_entries,
        'user_form_element_plugins': user_form_element_plugins,
        'user_form_handler_plugins': user_form_handler_plugins,
        'assembled_form': assembled_form,
        'form_element_entry_formset': form_element_entry_formset,
        'fobi_theme': theme,
        'collection_quota': request.user.collection_value,
        'user_locations_count': user_locations_count,
        'event_location_quota': event_location_quota,
    }

    # if not template_name:
    #     template_name = theme.edit_form_entry_template

    template_name = 'bootstrap3/edit_form_view.html'

    return render(request, template_name, context)


logger = logging.getLogger(__name__)


@login_required
def dashboard(request, theme=None, template_name=None):
    """Dashboard.

    :param django.http.HttpRequest request:
    :param fobi.base.BaseTheme theme: Theme instance.
    :param string template_name:
    :return django.http.HttpResponse:
    """
    form_entries = Event._default_manager \
                        .filter(user__pk=request.user.pk) \
                        .select_related('user')

    context = {
        'form_entries': form_entries,
        'form_importers': get_form_impoter_plugin_urls(),
    }

    # If given, pass to the template (and override the value set by
    # the context processor.
    if theme:
        context.update({'fobi_theme': theme})

    if not template_name:
        theme = get_theme(request=request, as_instance=True)
        template_name = theme.dashboard_template

    return render(request, template_name, context)


class EventDetailInvitati(LoginRequiredMixin, DetailView):
    """Organiser can view a list of his events"""
    model = EmailApp
    template_name = 'events/event_detail_invitati.html'
    slug_field = 'secret'
    slug_url_kwarg = 'secret'

    def get_context_data(self, **kwargs):
        da = self.object
        print(da)
        context = super().get_context_data(**kwargs)
        context['event'] = self.object.event
        context['locations'] = Location.objects.filter(
            event__title=self.object.event)
        context['anas'] = FormElementEntry.objects.filter(
            form_entry_id=self.object.pk)
        print('Form: ', context['anas'])
        context['collections'] = assemble_form_class(
            self.object.event,
        )
        context['das'] = EmailApp.objects.values_list('event__title', flat=True)[6]
        print('das: ', context['das'])
        # context['collections'] = self.get_form()
        print('collections: ', context['collections'])
        return context


def view_form_entry(
        request,
        # form_entry_slug,
        secret,
        theme=None,
        template_name=None):
    """View created form.

    :param django.http.HttpRequest request:
    :param string form_entry_slug:
    :param fobi.base.BaseTheme theme: Theme instance.
    :param string template_name:
    :return django.http.HttpResponse:
    """
    secrets = EmailApp.objects.filter(secret=secret)

    try:
        # kwargs = {'slug': form_entry_slug}
        kwargs = {'emailapp': secrets}
        if not request.user.is_authenticated():
            kwargs.update({'is_public': True})
        form_entry = Event._default_manager.select_related('user') \
                          .get(**kwargs)
    except ObjectDoesNotExist as err:
        raise Http404("Form entry not found.")

    form_element_entries = form_entry.formelemententry_set.all()[:]

    # This is where the most of the magic happens. Our form is being built
    # dynamically.
    form_cls = assemble_form_class(
        form_entry,
        form_element_entries=form_element_entries,
        request=request
    )

    if request.method == 'POST':
        form = form_cls(request.POST, request.FILES)

        # Fire pre form validation callbacks
        fire_form_callbacks(form_entry=form_entry,
                            request=request, form=form,
                            stage=CALLBACK_BEFORE_FORM_VALIDATION)

        if form.is_valid():
            # Fire form valid callbacks, before handling submitted plugin
            # form data.
            form = fire_form_callbacks(
                form_entry=form_entry,
                request=request,
                form=form,
                stage=CALLBACK_FORM_VALID_BEFORE_SUBMIT_PLUGIN_FORM_DATA
            )

            # Fire plugin processors
            form = submit_plugin_form_data(
                form_entry=form_entry,
                invitee=secrets,
                request=request,
                form=form
            )

            # Fire form valid callbacks
            form = fire_form_callbacks(form_entry=form_entry,
                                       request=request, form=form,
                                       stage=CALLBACK_FORM_VALID)

            # Run all handlers
            handler_responses, handler_errors = run_form_handlers(
                form_entry=form_entry,
                invitee=secret,
                request=request,
                form=form,
                form_element_entries=form_element_entries
            )

            # Warning that not everything went ok.
            if handler_errors:
                for handler_error in handler_errors:
                    messages.warning(
                        request,
                        ("Error occurred: {0}.").format(handler_error)
                    )

            # Fire post handler callbacks
            fire_form_callbacks(
                form_entry=form_entry,
                request=request,
                form=form,
                stage=CALLBACK_FORM_VALID_AFTER_FORM_HANDLERS
            )

            messages.info(
                request,
                ("Form {0} was submitted successfully.").format(
                    form_entry.title
                )
            )
            return redirect(
                reverse('events:fobi.form_entry_submitted',
                        args=[form_entry.slug])
            )
        else:
            # Fire post form validation callbacks
            fire_form_callbacks(form_entry=form_entry, request=request,
                                form=form, stage=CALLBACK_FORM_INVALID)

    else:
        # Providing initial form data by feeding entire GET dictionary
        # to the form, if ``GET_PARAM_INITIAL_DATA`` is present in the
        # GET.
        kwargs = {}
        if GET_PARAM_INITIAL_DATA in request.GET:
            kwargs = {'initial': request.GET}
        form = form_cls(**kwargs)

    # In debug mode, try to identify possible problems.
    if DEBUG:
        form.as_p()
    else:
        try:
            form.as_p()
        except Exception as err:
            logger.error(err)

    theme = get_theme(request=request, as_instance=True)
    theme.collect_plugin_media(form_element_entries)

    context = {
        'form': form,
        'form_entry': form_entry,
        'fobi_theme': theme,
        'fobi_form_title': form_entry.title,
    }

    if not template_name:
        # template_name = theme.view_form_entry_template
        template_name = 'events/event_detail_invitati.html'

    return render(request, template_name, context)


def view_form_entry_public(
        request,
        form_entry_slug,
        # secret,
        theme=None,
        template_name=None):
    """View created form.

    :param django.http.HttpRequest request:
    :param string form_entry_slug:
    :param fobi.base.BaseTheme theme: Theme instance.
    :param string template_name:
    :return django.http.HttpResponse:
    """
    # secrets = EmailApp.objects.filter(secret=secret)

    try:
        kwargs = {'slug': form_entry_slug}
        # kwargs = {'emailapp': secrets}
        # if not request.user.is_authenticated():
        #     kwargs.update({'is_public': True})
        form_entry = Event._default_manager.select_related('user') \
                          .get(**kwargs)
    except ObjectDoesNotExist as err:
        raise Http404("Form entry not found.")

    form_element_entries = form_entry.formelemententry_set.all()[:]

    # This is where the most of the magic happens. Our form is being built
    # dynamically.
    form_cls = assemble_form_class(
        form_entry,
        form_element_entries=form_element_entries,
        request=request
    )

    if request.method == 'POST':
        form = form_cls(request.POST, request.FILES)

        # Fire pre form validation callbacks
        fire_form_callbacks(form_entry=form_entry,
                            request=request, form=form,
                            stage=CALLBACK_BEFORE_FORM_VALIDATION)

        if form.is_valid():
            # Fire form valid callbacks, before handling submitted plugin
            # form data.
            form = fire_form_callbacks(
                form_entry=form_entry,
                request=request,
                form=form,
                stage=CALLBACK_FORM_VALID_BEFORE_SUBMIT_PLUGIN_FORM_DATA
            )

            # Fire plugin processors
            form = submit_plugin_form_data(
                form_entry=form_entry,
                # invitee=secrets,
                request=request,
                form=form
            )

            # Fire form valid callbacks
            form = fire_form_callbacks(form_entry=form_entry,
                                       request=request, form=form,
                                       stage=CALLBACK_FORM_VALID)

            # Run all handlers
            handler_responses, handler_errors = run_form_handlers(
                form_entry=form_entry,
                # invitee=secret,
                request=request,
                form=form,
                form_element_entries=form_element_entries
            )

            # Warning that not everything went ok.
            if handler_errors:
                for handler_error in handler_errors:
                    messages.warning(
                        request,
                        ("Error occurred: {0}.").format(handler_error)
                    )

            # Fire post handler callbacks
            fire_form_callbacks(
                form_entry=form_entry,
                request=request,
                form=form,
                stage=CALLBACK_FORM_VALID_AFTER_FORM_HANDLERS
            )

            messages.info(
                request,
                ("Form {0} was submitted successfully.").format(
                    form_entry.title
                )
            )
            return redirect(
                reverse('events:fobi.form_entry_submitted',
                        args=[form_entry.slug])
            )
        else:
            # Fire post form validation callbacks
            fire_form_callbacks(form_entry=form_entry, request=request,
                                form=form, stage=CALLBACK_FORM_INVALID)

    else:
        # Providing initial form data by feeding entire GET dictionary
        # to the form, if ``GET_PARAM_INITIAL_DATA`` is present in the
        # GET.
        kwargs = {}
        if GET_PARAM_INITIAL_DATA in request.GET:
            kwargs = {'initial': request.GET}
        form = form_cls(**kwargs)

    # In debug mode, try to identify possible problems.
    if DEBUG:
        form.as_p()
    else:
        try:
            form.as_p()
        except Exception as err:
            logger.error(err)

    theme = get_theme(request=request, as_instance=True)
    theme.collect_plugin_media(form_element_entries)

    context = {
        'form': form,
        'form_entry': form_entry,
        'fobi_theme': theme,
        'fobi_form_title': form_entry.title,
    }

    if not template_name:
        # template_name = theme.view_form_entry_template
        template_name = 'events/event_detail_invitati.html'

    return render(request, template_name, context)


@login_required
def delete_form_entry(request, form_entry_id, template_name=None):
    """Delete form entry.

    :param django.http.HttpRequest request:
    :param int form_entry_id:
    :param string template_name:
    :return django.http.HttpResponse:
    """
    try:
        obj = FormEntry._default_manager \
            .get(pk=form_entry_id, user__pk=request.user.pk)
    except ObjectDoesNotExist:
        raise Http404("Form entry not found.")

    obj.delete()

    messages.info(
        request,
        ('The form "{0}" was deleted successfully.').format(obj.name)
    )

    return redirect('events:fobi.dashboard')


@login_required
def add_form_element_entry(request,
                           form_entry_id,
                           form_element_plugin_uid,
                           theme=None,
                           template_name=None):
    """Add form element entry.

    :param django.http.HttpRequest request:
    :param int form_entry_id:
    :param int form_element_plugin_uid:
    :param fobi.base.BaseTheme theme: Theme instance.
    :param string template_name:
    :return django.http.HttpResponse:
    """
    try:
        form_entry = Event._default_manager \
                          .prefetch_related('formelemententry_set') \
                          .get(pk=form_entry_id)
    except ObjectDoesNotExist:
        raise Http404("Form entry not found.")

    form_elements = form_entry.formelemententry_set.all()

    user_form_element_plugin_uids = get_user_form_field_plugin_uids(
        request.user
    )

    if form_element_plugin_uid not in user_form_element_plugin_uids:
        raise Http404("Plugin does not exist or you are not allowed "
                      "to use this plugin!")

    form_element_plugin_cls = form_element_plugin_registry.get(
        form_element_plugin_uid
    )
    form_element_plugin = form_element_plugin_cls(user=request.user)
    form_element_plugin.request = request

    form_element_plugin_form_cls = form_element_plugin.get_form()
    form = None

    obj = FormElementEntry()
    obj.form_entry = form_entry
    obj.plugin_uid = form_element_plugin_uid
    obj.user = request.user

    save_object = False

    if form_elements.count() < form_entry.collection_quota:
        # If plugin doesn't have a form
        if not form_element_plugin_form_cls:
            save_object = True

        # If POST
        elif request.method == 'POST':
            # If element has a form
            form = form_element_plugin.get_initialised_create_form_or_404(
                data=request.POST,
                files=request.FILES
            )
            form.validate_plugin_data(form_elements, request=request)
            if form.is_valid():
                # Saving the plugin form data.
                form.save_plugin_data(request=request)

                # Getting the plugin data.
                obj.plugin_data = form.get_plugin_data(request=request)

                if form_elements.count() < form_entry.collection_quota:
                    save_object = True
                else:
                    return HttpResponseRedirect(
                        reverse('events:list'))

        # If not POST
        else:
            form = form_element_plugin.get_initialised_create_form_or_404()
    else:
        return HttpResponseRedirect(
            reverse('events:list'))

    if save_object:
        # Handling the position
        position = 1
        records = FormElementEntry.objects.filter(form_entry=form_entry) \
                                  .aggregate(models.Max('position'))
        if records:
            try:
                position = records['{0}__max'.format('position')] + 1

            except TypeError:
                pass

        obj.position = position

        # Save the object.
        obj.save()

        messages.info(
            request,
            ('The form element plugin "{0}" was added '
             'successfully.').format(form_element_plugin.name)
        )
        return redirect(
            # "{0}?active_tab=tab-form-elements".format(
            reverse('events:fobi.edit_form_entry',
                    kwargs={'form_entry_id': form_entry_id})
        )
        # )

    context = {
        'form': form,
        'form_entry': form_entry,
        'form_element_plugin': form_element_plugin,
    }

    # If given, pass to the template (and override the value set by
    # the context processor.
    # if theme:
    #     context.update({'fobi_theme': theme})

    if not template_name:
        if not theme:
            theme = get_theme(request=request, as_instance=True)
        template_name = theme.add_form_element_entry_template
    # else:
    #     template_name = 'k.html'

    return render(request, template_name, context)
    # else:
    #     return reverse_lazy('events:list')


# *****************************************************************************
# **************************** Edit form element entry ************************
# *****************************************************************************


@login_required
def edit_form_element_entry(request,
                            form_element_entry_id,
                            theme=None,
                            template_name=None):
    """Edit form element entry.

    :param django.http.HttpRequest request:
    :param int form_element_entry_id:
    :param fobi.base.BaseTheme theme: Theme instance.
    :param string template_name:
    :return django.http.HttpResponse:
    """
    try:
        obj = FormElementEntry._default_manager \
                              .select_related('form_entry',
                                              'form_entry__user') \
                              .get(pk=form_element_entry_id,
                                   form_entry__user__pk=request.user.pk)
    except ObjectDoesNotExist:
        raise Http404("Form element entry not found.")

    form_entry = obj.form_entry
    form_element_plugin = obj.get_plugin(request=request)
    form_element_plugin.request = request

    FormElementPluginForm = form_element_plugin.get_form()
    form = None

    if not FormElementPluginForm:
        messages.info(
            request,
            ('The form element plugin "{0}" '
             'is not configurable!').format(form_element_plugin.name)
        )
        return redirect('events:fobi.edit_form_entry', form_entry_id=form_entry.pk)

    elif request.method == 'POST':
        form = form_element_plugin.get_initialised_edit_form_or_404(
            data=request.POST,
            files=request.FILES
        )

        form_elements = FormElementEntry._default_manager \
                                        .select_related('form_entry',
                                                        'form_entry__user') \
                                        .exclude(pk=form_element_entry_id) \
                                        .filter(form_entry=form_entry)

        form.validate_plugin_data(form_elements, request=request)

        if form.is_valid():
            # Saving the plugin form data.
            form.save_plugin_data(request=request)

            # Getting the plugin data.
            obj.plugin_data = form.get_plugin_data(request=request)

            # Save the object.
            obj.save()

            messages.info(
                request,
                ('The form element plugin "{0}" was edited '
                 'successfully.').format(form_element_plugin.name)
            )

            return redirect('events:fobi.edit_form_entry',
                            form_entry_id=form_entry.pk)

    else:
        form = form_element_plugin.get_initialised_edit_form_or_404()

    form_element_plugin = obj.get_plugin(request=request)
    form_element_plugin.request = request

    context = {
        'form': form,
        'form_entry': form_entry,
        'form_element_plugin': form_element_plugin,
    }
    print(form)
    # If given, pass to the template (and override the value set by
    # the context processor.
    if theme:
        context.update({'fobi_theme': theme})

    if not template_name:
        if not theme:
            theme = get_theme(request=request, as_instance=True)
        template_name = theme.edit_form_element_entry_template

    return render(request, template_name, context)


# *****************************************************************************
# **************************** Delete form element entry **********************
# *****************************************************************************
def _delete_plugin_entry_dragos(request,
                                entry_id,
                                entry_model_cls,
                                get_user_plugin_uids_func,
                                message,
                                html_anchor):
    """Abstract delete entry.

    :param django.http.HttpRequest request:
    :param int entry_id:
    :param fobi.models.AbstractPluginEntry entry_model_cls: Subclass of
        ``fobi.models.AbstractPluginEntry``.
    :param callable get_user_plugin_uids_func:
    :param str message:
    :return django.http.HttpResponse:
    """
    try:
        obj = entry_model_cls._default_manager \
                             .select_related('form_entry') \
                             .get(pk=entry_id,
                                  form_entry__user__pk=request.user.pk)
    except ObjectDoesNotExist:
        raise Http404(("{0} not found.").format(
            entry_model_cls._meta.verbose_name)
        )

    form_entry = obj.form_entry
    plugin = obj.get_plugin(request=request)
    plugin.request = request

    plugin._delete_plugin_data()

    obj.delete()

    messages.info(request, message.format(plugin.name))

    redirect_url = reverse(
        'events:fobi.edit_form_entry', kwargs={'form_entry_id': form_entry.pk}
    )
    return redirect("{0}{1}".format(redirect_url, html_anchor))


@login_required
def delete_form_element_entry(request, form_element_entry_id):
    """Delete form element entry.

    :param django.http.HttpRequest request:
    :param int form_element_entry_id:
    :return django.http.HttpResponse:
    """
    return _delete_plugin_entry(
        request=request,
        entry_id=form_element_entry_id,
        entry_model_cls=FormElementEntry,
        get_user_plugin_uids_func=get_user_form_field_plugin_uids,
        message=(
            'The form element plugin "{0}" was deleted successfully.'
        ),
        html_anchor='?active_tab=tab-form-elements'
    )


def form_entry_submitted(request, form_entry_slug=None, template_name=None):
    """Form entry submitted.

    :param django.http.HttpRequest request:
    :param string form_entry_slug:
    :param string template_name:
    :return django.http.HttpResponse:
    """
    try:
        kwargs = {'slug': form_entry_slug}
        # if not request.user.is_authenticated():
        #     kwargs.update({'is_public': True})
        form_entry = Event._default_manager \
            .select_related('user') \
            .get(**kwargs)
    except ObjectDoesNotExist:
        raise Http404("Form entry not found.")

    context = {
        'form_entry_slug': form_entry_slug,
        'form_entry': form_entry
    }

    if not template_name:
        theme = get_theme(request=request, as_instance=True)
        template_name = theme.form_entry_submitted_template

    return render(request, template_name, context)
