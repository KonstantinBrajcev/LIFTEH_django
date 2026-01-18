from django.contrib import admin
from LIFTEH.models import Object, Avr, Service, Diagnostic, Dogovor


class ObjectAdmin(admin.ModelAdmin):
    list_display = ('customer', 'address', 'model')


class AvrAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_info', 'problem')

    def customer_info(self, obj):
        return obj.object.customer if obj.object else '-'
    customer_info.short_description = 'Клиент'  # Заголовок колонки
    customer_info.admin_order_field = 'object__customer'  # Сортировка по полю


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('customer', 'address', 'model')


admin.site.register(Object, ObjectAdmin)
admin.site.register(Avr, AvrAdmin)
admin.site.register(Service)
admin.site.register(Diagnostic)


@admin.register(Dogovor)
class DogovorAdmin(admin.ModelAdmin):
    # Убираем 'objects' из list_display, так как это обратная связь
    list_display = ('number', 'formatted_date', 'customer',
                    'financing_display', 'longtime_display', 'is_active')
    list_filter = ('financing', 'longtime', 'is_active', 'date')
    search_fields = ('number', 'customer')

    # Метод для форматированной даты
    def formatted_date(self, obj):
        return obj.get_formatted_date()
    formatted_date.short_description = 'Дата договора'
    formatted_date.admin_order_field = 'date'

    # Метод для отображения финансирования
    def financing_display(self, obj):
        return obj.get_financing_display_name()
    financing_display.short_description = 'Финансирование'

    # Метод для отображения лонгирования
    def longtime_display(self, obj):
        return obj.get_longtime_display_name()
    longtime_display.short_description = 'Лонгирование'

    fieldsets = (
        ('Основная информация', {
            'fields': ('customer', 'number', 'date')
        }),
        ('Детали договора', {
            'fields': ('financing', 'longtime', 'is_active')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')
