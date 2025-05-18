from django import template

register = template.Library()


@register.filter
def get_month_name(month):
    """Возвращает название месяца по номеру"""
    month = int(month)  # Преобразуем строку в число
    month_names = {
        1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
        5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
        9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
    }
    return month_names.get(month, f"M{month}")


@register.filter
def get_field(form, field_name):
    """Получает поле формы по имени"""
    return form[field_name]


@register.filter
def split(value, arg=" "):
    return value.split(arg)


@register.filter
def get_field_value(form, field_name):
    """Получает значение поля формы по имени"""
    return form[field_name].value() if field_name in form.fields else ""


@register.filter
def format_decimal(value):
    """Форматирует Decimal для HTML input type=number"""
    if value is None:
        return ""
    return str(value).replace(',', '.')  # Заменяем запятую на точку
