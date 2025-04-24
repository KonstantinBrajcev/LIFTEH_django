from django.contrib import admin
from LIFTEH.models import Object, Avr, Service, Work, Switch

# class ObjectAdmin(admin.ModelAdmin):
#     list_display = ('customer', 'address', 'model')

# class AvrAdmin(admin.ModelAdmin):
#     list_display = ('insert_date', 'problem', 'work_id')

admin.site.register(Object)
admin.site.register(Avr)
admin.site.register(Service)
admin.site.register(Work)
admin.site.register(Switch)