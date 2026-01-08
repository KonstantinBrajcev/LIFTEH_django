from django import template

register = template.Library()


@register.simple_tag
def modify_query(**new_params):
    from django.http import QueryDict
    import urllib.parse

    request = template.resolve_context('request')
    current_params = request.GET.copy()

    # Обновляем параметры
    for key, value in new_params.items():
        if key == 'sort':
            current_sort = current_params.get('sort')
            current_order = current_params.get('order', 'asc')
            if value == current_sort:
                # Меняем порядок сортировки
                new_order = 'desc' if current_order == 'asc' else 'asc'
                current_params['order'] = new_order
            else:
                # Новая сортировка
                current_params['sort'] = value
                current_params['order'] = 'asc'
        else:
            current_params[key] = value

    return current_params.urlencode()
