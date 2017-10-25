from import_export import resources
from .models import EmailApp


class EmailResource(resources.ModelResource):
    class Meta:
        model = EmailApp
        fields = ('name', 'email',)
