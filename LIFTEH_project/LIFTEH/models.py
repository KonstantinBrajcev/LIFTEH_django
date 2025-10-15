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
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    folder_id = models.CharField(max_length=50, default='', blank=True)


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
    RESULT_CHOICES = [
        (0, 'Отправлено КП'),
        (1, 'Согласовано'),
        (2, 'Выполнено'),
        (3, 'Отправлен АКТ'),
    ]
        
    insert_date = models.DateTimeField(default=timezone.now)
    object = models.ForeignKey(Object, on_delete=models.CASCADE)
    problem = models.CharField(max_length=500, default='')
    # work_id = models.IntegerField(null=True, blank=True)
    # Разрешить NULL и добавить default
    work_id = models.IntegerField(null=True, blank=True, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    result = models.IntegerField(null=True, blank=True, choices=RESULT_CHOICES, default=None)
    # result = models.CharField(max_length=3, null=True, blank=True)

    def __str__(self):
        return f"АВР #{self.id} - {self.object.customer}"

    class Meta:
        verbose_name = 'Акт ВР'
        verbose_name_plural = 'Акты ВР'

class Work(models.Model):
    UNIT_CHOICES = [
        ('1', 'шт.'),
        ('2', 'комп.'),
        ('3', 'л.'),
        ('4', 'кг.'),
        ('5', 'м.'),
    ]
    avr = models.ForeignKey(Avr, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    quantity = models.IntegerField(default=1)


class Diagnostic(models.Model):
    object = models.ForeignKey(
        Object, on_delete=models.CASCADE, related_name='diagnostics')
    insert_date = models.DateTimeField('Дата ввода', default=timezone.now)
    end_date = models.DateTimeField('Дата окончания', default=timezone.now)
    fact_date = models.DateTimeField('Дата проведения', null=True, blank=True)
    result = models.IntegerField('Результат', null=True, blank=True)

    def __str__(self):
        return f"Диагностика {self.object.name} от {self.insert_date}"


class Switch(models.Model):
    power = models.BooleanField(default=False)

    def __str__(self):
        return "Включено" if self.power else "Выключено"

class Problem(models.Model):
    name = models.CharField(max_length=255, verbose_name="Наименование задачи")
    created_date = models.DateField(auto_now_add=True, verbose_name="Дата создания")
    is_completed = models.BooleanField(default=False, verbose_name="Выполнено")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

class AccessUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    object = models.ForeignKey('Object', on_delete=models.CASCADE, verbose_name="Объект")
    
    class Meta:
        verbose_name = "Доступ пользователя"
        verbose_name_plural = "Доступы пользователей"
        unique_together = ('user', 'object')  # Уникальная связь пользователь-объект
    
    def __str__(self):
        return f"{self.user.username} - {self.object.customer}"