from django.contrib import admin
from LIFTEH.models import Object, Avr, Service, Diagnostic


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
