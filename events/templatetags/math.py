from django import template

# Django template custom math filters
# Ref : https://code.djangoproject.com/ticket/361
register = template.Library()


def div(arg):
    "Divides the value by the arg"
    return int(12 / int(arg))


register.filter('div', div)
