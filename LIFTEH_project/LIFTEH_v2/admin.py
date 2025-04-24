from django.contrib import admin
from LIFTEH.models import Object, Avr

class ObjectAdmin(admin.ModelAdmin):
    list_display = ('customer', 'address', 'model')

class AvrAdmin(admin.ModelAdmin):
    list_display = ('insert_date', 'problem', 'work_id')

admin.site.register(Object, ObjectAdmin)
admin.site.register(Avr, AvrAdmin)