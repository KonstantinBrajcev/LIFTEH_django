from django import template

register = template.Library()


@register.simple_tag
def calculate_totals(grouped_objects):
    total_objects = 0
    total_green = 0
    total_yellow = 0
    total_red = 0
    total_gray = 0

    for group in grouped_objects:
        total_objects += len(group['objects'])
        total_green += group['color_counts']['green']
        total_yellow += group['color_counts']['yellow']
        total_red += group['color_counts']['red']
        total_gray += group['color_counts']['gray']

    return {
        'total_objects': total_objects,
        'total_green': total_green,
        'total_yellow': total_yellow,
        'total_red': total_red,
        'total_gray': total_gray,
    }
