from django.contrib import admin
# Register your models here.
from .models import Event


# The Admin view for the Events App
class EventAdmin(admin.ModelAdmin):
    fields = (
        'title',
        'description',)
    list_display = (
        'title',
        'description',)


admin.site.register(Event, EventAdmin)
