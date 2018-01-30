from django.contrib import admin
# Register your models here.
from .models import (
    Event,
    Location,
    EmailApp,
    # Options,
    # OptionField,
    FormEntry,
    FormElementEntry,
    # FormFieldsetEntry,
    FormHandlerEntry
)

from .forms import FormElementEntryForm, FormHandlerEntryForm


# The Admin view for the Events App
class EventAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Quotas',
            {'classes': ('collapse',),
             'fields': (
                'location_quota',
                'collection_quota',
                'email_quota')}),
        ('General',
            {'fields': (
                'title',
                'is_public',
                'image',
                'description',
                'user')})
    )
    # list_display = (
    #     'title',
    #     'description',
    #     'user')
    list_display = [f.name for f in Event._meta.fields]


class LocationAdmin(admin.ModelAdmin):
    fields = (
        'event',
        'l_title',
        'l_date',
        'address',
    )
    list_display = (
        'l_title',
        'event',)


class EmailAppAdmin(admin.ModelAdmin):
    fields = (
        'event',
        'name',
        'email',
        'secret',)
    # list_display = (
    #     'title',
    #     'description',
    #     'user')
    list_display = [f.name for f in EmailApp._meta.fields]


admin.site.register(Event, EventAdmin)
admin.site.register(EmailApp, EmailAppAdmin)
admin.site.register(Location, LocationAdmin)


# class FormElementEntryInlineAdmin(admin.TabularInline):
#     """FormElementEntry inline admin."""

#     model = FormElementEntry
#     form = FormElementEntryForm
#     fields = ('form_entry', 'plugin_uid', 'plugin_data', 'position',)
#     extra = 0
class FormElementEntryAdmin(admin.ModelAdmin):
    fields = ('form_entry', 'plugin_uid', 'plugin_data', 'position',)
    # list_display = (
    #     'title',
    #     'description',
    #     'user')
    list_display = [f.name for f in FormElementEntry._meta.fields]


admin.site.register(FormElementEntry, FormElementEntryAdmin)

# class FormHandlerEntryInlineAdmin(admin.TabularInline):
#     """FormHandlerEntry inline admin."""

#     model = FormHandlerEntry
#     form = FormHandlerEntryForm
#     fields = ('form_entry', 'plugin_uid', 'plugin_data',)
#     extra = 0


class FormHandlerEntryAdmin(admin.ModelAdmin):
    fields = ('form_entry', 'plugin_uid', 'plugin_data',)
    # list_display = (
    #     'title',
    #     'description',
    #     'user')
    list_display = [f.name for f in FormHandlerEntry._meta.fields]


admin.site.register(FormHandlerEntry, FormHandlerEntryAdmin)


class FormEntryAdmin(admin.ModelAdmin):
    """FormEntry admin."""

    list_display = (
        'id',
        'name',
        'slug',
        'event',
        'user',
        'is_public',
        'created',
        'updated',)
    list_editable = ('is_public',)  # 'is_cloneable',)
    list_filter = ('is_public',)  # 'is_cloneable',)
    readonly_fields = ('slug',)
    radio_fields = {"user": admin.VERTICAL}
    fieldsets = (
        ("Form", {
            'fields': ('name', 'event', 'is_public',)  # 'is_cloneable',)
        }),
        ("Custom", {
            'classes': ('collapse',),
            'fields': ('success_page_title', 'success_page_message',)
        }),
        ("User", {
            'classes': ('collapse',),
            'fields': ('user',)
        }),
        ('Additional', {
            'classes': ('collapse',),
            'fields': ('slug',)
        }),
    )
    # inlines = [FormElementEntryInlineAdmin, FormHandlerEntryInlineAdmin]

    # class Meta(object):
    #     """Meta."""

    #     app_label = _('Fobi')


admin.site.register(FormEntry, FormEntryAdmin)
