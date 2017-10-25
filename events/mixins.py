from django.http import JsonResponse
from django.forms.models import model_to_dict


class AjaxFormMixin(object):
    def form_invalid(self, form):
        response = super(AjaxFormMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super(AjaxFormMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'title': form.instance.title,
                'description': form.instance.description,
            }
            return JsonResponse(data)
        else:
            return response
