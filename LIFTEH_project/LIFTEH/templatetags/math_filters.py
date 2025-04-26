from django import template

register = template.Library()


@register.filter(name='mul')
def mul(value, arg):
    """Умножает значение на аргумент"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0
