# templatetags/object_plural.py
from django import template

register = template.Library()

@register.filter
def object_plural(value):
    """
    Возвращает правильную форму слова "объект" для русского языка
    """
    try:
        value = int(value)
        if value % 10 == 1 and value % 100 != 11:
            return "объект"
        elif 2 <= value % 10 <= 4 and (value % 100 < 10 or value % 100 >= 20):
            return "объекта"
        else:
            return "объектов"
    except (ValueError, TypeError):
        return "объектов"