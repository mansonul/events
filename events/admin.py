from django.contrib import admin
# Register your models here.
from .models import Event


# The Admin view for the Events App
class EventAdmin(admin.ModelAdmin):
    fields = (
        'title',
        'image',
        'description',
        'user',)
    list_display = (
        'title',
        'description',
        'user')


admin.site.register(Event, EventAdmin)
