<<<<<<< HEAD
from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
=======
from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
>>>>>>> bubuka
    return dictionary.get(key)