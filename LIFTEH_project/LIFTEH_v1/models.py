from asyncio.windows_events import NULL
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Object(models.Model):
    # СТРОКИ ТАБЛИЦЫ ОБЬЕКТЫ
    customer = models.CharField(max_length=255, default='')
    address = models.CharField(max_length=255, default='')
    model = models.CharField(max_length=255, default='')
    work = models.CharField(max_length=20, default='')
    phone = models.CharField(max_length=20, default='')
    name = models.CharField(max_length=255, default='')
    M1 = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    M2 = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    M3 = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    M4 = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    M5 = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    M6 = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    M7 = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    M8 = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    M9 = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    M10 = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    M11 = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    M12 = models.DecimalField(max_digits=12, decimal_places=2, null=True)


class Service(models.Model):
    object = models.ForeignKey(Object, on_delete=models.CASCADE)
    # service_date = models.DateField(default=timezone.now)
    service_date = models.DateTimeField(default=timezone.now)
    comments = models.TextField()
    result = models.CharField(max_length=200)
    foto = models.ImageField(upload_to='services_foto/',
                             null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"ТО для {self.object.customer} - {self.service_date}"
    
class Avr(models.Model):
    insert_date = models.DateTimeField(default=timezone.now)
    object = models.ForeignKey(Object, on_delete=models.CASCADE)
    problem = models.CharField(max_length=500, default='')
    work_id = models.CharField(max_length=20, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
