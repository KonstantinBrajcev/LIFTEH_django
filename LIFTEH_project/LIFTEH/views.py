from django.utils import timezone
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView
from django.views import View
from django.db import models, connection
from django.db.models import Sum, FloatField, F
from django.db.models.functions import Coalesce
from django.utils.timezone import now
from django.shortcuts import render
from LIFTEH.models import Object, Avr, Service, Work, Switch
from LIFTEH.forms import ObjectForm, ServiceForm, AvrForm, ObjectAvrForm
import re


class HomeView(TemplateView):
    template_name = 'home.html'


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('to')  # перенаправление на страницу 'to'
        else:
            return render(request, 'login.html', {'error': 'Неверный логин или пароль'})


@method_decorator(login_required, name='dispatch')
class ToView(TemplateView):
    template_name = 'to.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        month = self.request.GET.get('month', timezone.now().month)
        year = timezone.now().year

        selected_city = self.request.GET.get('city')  # выбранный город

        objects = Object.objects.all()
        objects = objects.filter(**{f'M{month}__isnull': False}).exclude(**{f'M{month}': 0})
        
                # Извлекаем города из адресов (уникально)
        city_set = set()
        for obj in objects:
            match = re.match(r'^(г\.п\.|ж/д ст\.|г\.|п\.|д\.)\s*[^,]+', obj.address)
            if match:
                city = match.group(0).strip()
                city_set.add(city)
        cities = sorted(city_set)

        # Фильтрация по выбранному городу
        if selected_city:
            objects = objects.filter(address__icontains=selected_city)

        service_records = {}
        for obj in objects:
            # Получаем первую запись для каждого объекта за текущий месяц
            # service_record = obj.service_set.filter(service_date__year=year, service_date__month=month).first()
            service_records[obj.id] = obj.service_set.filter(service_date__year=year, service_date__month=month).first()

        context['month'] = month
        context['objects'] = objects
        context['service_records'] = service_records
        context['cities'] = cities
        context['selected_city'] = selected_city

        context['avrs'] = Avr.objects.all()

        charts_view = ChartsView()
        charts_view.request = self.request
        context.update(charts_view.get_context_data())
        
        tasks_view = TasksView()
        tasks_view.request = self.request
        context.update(tasks_view.get_context_data())

        return context

# ---------- ГРАФИКИ ------------

class ChartsView(TemplateView):
    template_name = 'charts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # График №1 по месяцам (сумма по всем объектам)
        months = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6',
                  'M7', 'M8', 'M9', 'M10', 'M11', 'M12']
        month_names = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                       'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

        # Безопасное суммирование с преобразованием типов
        month_sums = []
        for month in months:
            total = Object.objects.aggregate(
                sum=Sum(F(month), output_field=models.FloatField())
            )['sum'] or 0
            month_sums.append(float(total))

        # Рассчитываем среднее значение по месяцам
        non_zero_months = [m for m in month_sums if m > 0]
        context['month_avg'] = round(
            sum(non_zero_months) / len(non_zero_months), 2) if non_zero_months else 0

        # График №2 по заказчикам (оптимизированный запрос)
        # График №2: Сумма по заказчикам
        customers_data = []
        unique_customers = Object.objects.values_list(
            'customer', flat=True).distinct()

        for customer in unique_customers:
            customer_total = 0.0
            # Суммируем все месяцы для каждого заказчика
            for month in months:
                month_sum = Object.objects.filter(customer=customer).aggregate(
                    sum=Coalesce(Sum(month, output_field=FloatField()), 0.0)
                )['sum']
                customer_total += float(month_sum)

            if customer_total > 0:  # Исключаем нулевые значения
                customers_data.append({
                    'customer': customer,
                    'total': customer_total
                })

        # Сортируем по убыванию суммы
        customers_data.sort(key=lambda x: x['total'], reverse=True)

        # График №3: Среднее значение по месяцам для каждого заказчика
        customers_avg = []
        months = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6',
                  'M7', 'M8', 'M9', 'M10', 'M11', 'M12']

        # Получаем всех уникальных заказчиков
        unique_customers = Object.objects.values('customer').distinct()

        for customer in unique_customers:
            customer_name = customer['customer']

            # Получаем все объекты для текущего заказчика
            customer_objects = Object.objects.filter(customer=customer_name)

            total_sum = 0
            total_non_null_months = 0

            for obj in customer_objects:
                for month in months:
                    month_value = getattr(obj, month)
                    if month_value is not None:
                        total_sum += float(month_value)
                        total_non_null_months += 1

            # Рассчитываем среднее значение (избегаем деления на 0)
            avg_value = total_sum / total_non_null_months if total_non_null_months > 0 else 0

            customers_avg.append({
                'customer': customer_name,
                'avg_value': round(avg_value, 2)  # Округляем до 2 знаков
            })

        # Сортируем по убыванию среднего значения
        customers_avg.sort(key=lambda x: x['avg_value'], reverse=True)

        # ИТОГО - Рассчитываем общую сумму
        total_sum_all = 0.0
        months = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6',
                  'M7', 'M8', 'M9', 'M10', 'M11', 'M12']

        for month in months:
            month_total = Object.objects.aggregate(
                sum=Coalesce(Sum(month, output_field=FloatField()), 0.0)
            )['sum']
            total_sum_all += float(month_total)

        # Рассчитываем среднее значение по всем данным графика №2
        # Рассчитываем среднее значение по всем данным графика
        avg_values = [item['avg_value']
                      for item in customers_avg if item['avg_value'] > 0]
        context['global_avg'] = round(
            sum(avg_values) / len(avg_values), 2) if avg_values else 0

        context.update({
            'month_names': month_names,
            'month_sums': month_sums,
            'customers': [c['customer'] for c in customers_data],
            'customer_totals': [c['total'] for c in customers_data],
            'customers_avg': customers_avg,
            'customers_count': len(customers_data),
            'total_sum_all': round(total_sum_all, 2)
        })
        # context['canvas_width'] = len(context['customers']) * 30
        return context
# ----------- ЗАДАЧИ -----------
class TasksView(TemplateView):
    template_name = 'tasks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            now = timezone.localtime(timezone.now())
            first_day = timezone.make_aware(
                timezone.datetime(now.year, now.month, 1))
            last_day = timezone.make_aware(timezone.datetime(
                now.year + 1, 1, 1) if now.month == 12 else
                timezone.datetime(now.year, now.month + 1, 1)
            )

            # 1. Объекты без техобслуживания
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT object_id 
                    FROM lifteh_service 
                    WHERE service_date >= %s AND service_date < %s
                """, [first_day, last_day])
                serviced_ids = [row[0] for row in cursor.fetchall()]

            objects_without_service = list(
                Object.objects.exclude(id__in=serviced_ids).values())

            # 2. Невыполненные АВР
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        o.customer, o.address, a.problem, 
                        CASE 
                            WHEN a.insert_date IS NULL THEN 'Дата не указана'
                            ELSE datetime(a.insert_date)
                        END as insert_date_str
                    FROM lifteh_avr a
                    JOIN lifteh_object o ON a.object_id = o.id
                    WHERE a.result IS NULL
                    ORDER BY a.insert_date
                """)
                unfinished_avr_data = [
                    {
                        'customer': row[0],
                        'address': row[1],
                        'problem': row[2],
                        'insert_date': row[3]
                    }
                    for row in cursor.fetchall()
                ]

            context.update({
                'objects_without_service': objects_without_service,
                'unfinished_avr_data': unfinished_avr_data,
                'now': now.strftime("%Y-%m-%d %H:%M:%S"),
                'first_day': first_day.strftime("%Y-%m-%d"),
                'last_day': last_day.strftime("%Y-%m-%d"),
                'service_count': len(serviced_ids),
                'avr_count': len(unfinished_avr_data),
            })

        except Exception as e:
            context['error'] = f"Ошибка: {str(e)}"

        return context
    
# ------ РАБОТА С ОБЪЕКТАМИ ------
def objects_edit(request, pk):
    servicing = get_object_or_404(Object, pk=pk)
    if request.method == "POST":
        form = ObjectForm(request.POST, instance=servicing)
        if form.is_valid():
            form.save()
            return redirect(reverse('to') + '#service')
    else:
        form = ObjectForm(instance=servicing)
    return render(request, 'object_edit.html', {'form': form})


def object_add(request):
    if request.method == "POST":
        form = ObjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('to') + '#service')
    else:
        form = ObjectForm()
    return render(request, 'object_add.html', {'form': form})


def object_delete(request, pk):
    obj = get_object_or_404(Object, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect(reverse('to') + '#service')
    return redirect(reverse('to') + '#service')


# ------ РАБОТА С АВР ------
# @login_required
def avr_add(request, pk):
    current_datetime = timezone.now()
    obj = get_object_or_404(Object, id=pk)

    if request.method == 'POST':
        form = AvrForm(request.POST)
        
        if form.is_valid():
            avr = form.save(commit=False)
            avr.user = request.user  # Устанавливаем текущего пользователя
            avr.object = obj
            avr.save()

            # Сохраняем работы
            worknames = request.POST.getlist('workname')
            units = request.POST.getlist('unit')
            quantities = request.POST.getlist('quantity')
            
            for workname, unit, quantity in zip(worknames, units, quantities):
                if workname:  # Проверяем, что название работы не пустое
                    Work.objects.create(
                        avr=avr,
                        name=workname,
                        unit=unit,
                        quantity=quantity
                    )

            return redirect(reverse('to') + '#acts')
        else:
            print(form.errors)  # Выводим ошибки формы в консоль
    else:
        form = AvrForm()
    
    return render(request, 'avr_add.html', {'form': form, 'object': obj, 'current_datetime': current_datetime})


def avr_edit(request, pk):
    avr = get_object_or_404(Avr, pk=pk)
    current_datetime = timezone.now()
    if request.method == 'POST':
        avr.insert_date = request.POST['insert_date']
        avr.problem = request.POST['problem']
        # avr.work_id = request.POST['work_id']
        work_id = request.POST['work_id']
        avr.work_id = work_id if work_id else None
        avr.save()
        return redirect(reverse('to') + '#acts')  # Замените 'to' на ваш URL
    return render(request, 'avr_edit.html', {'avr': avr, 'current_datetime': current_datetime})

def avr_delete(request, pk):
    avr = get_object_or_404(Avr, pk=pk)
    avr.delete()
    return redirect(reverse('to') + '#acts')



def object_avr_add(request):
    if request.method == 'POST':
        form = ObjectAvrForm(request.POST)
        if form.is_valid():
            # Сохранение объекта
            obj = Object(
                customer=form.cleaned_data['customer'],
                address=form.cleaned_data['address']
            )
            obj.save()

            # Сохранение АВР
            avr = Avr(
                # insert_date=form.cleaned_data['insert_date'],
                insert_date = timezone.now(),
                problem=form.cleaned_data['problem'],
                object=obj,
                user=request.user
            )
            avr.save()

            # Сохраняем работы
            worknames = request.POST.getlist('workname')
            units = request.POST.getlist('unit')
            quantities = request.POST.getlist('quantity')
            
            for workname, unit, quantity in zip(worknames, units, quantities):
                if workname:  # Проверяем, что название работы не пустое
                    Work.objects.create(
                        avr=avr,
                        name=workname,
                        unit=unit,
                        quantity=quantity
                    )

            return redirect(reverse('to') + '#acts')
    else:
        form = ObjectAvrForm()

    return render(request, 'object_avr_add.html', {'form': form})


# ------ РАБОТА С ОБСЛУЖИВАНИЕМ ------
@login_required
def service_add(request, object_id):
    obj = get_object_or_404(Object, id=object_id)
    services = Service.objects.filter(object=obj)
    current_datetime = timezone.now()

    if request.method == 'POST':
        # Используем форму для создания нового объекта обслуживания
        form = ServiceForm(request.POST, request.FILES, object_id=object_id)

        if form.is_valid():
            # Сохраняем форму с добавлением пользователя
            form.save(user=request.user)
            # Перенаправляем на список объектов или куда-то еще
            return redirect(reverse('to') + '#service')
        else:
            # Если форма невалидна, отображаем ошибки
            return HttpResponse("Форма невалидна!")
        
    # Если запрос GET, выводим пустую форму
    form = ServiceForm()
    return render(request, 'service_add.html', {'form': form, 'object': obj, 'services': services, 'current_datetime': current_datetime})

class SwitchView(View):
    def get(self, request):
        # Получаем или создаём состояние устройства
        state, created = Switch.objects.get_or_create(id=1)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'power': state.power})
        
        return render(request, 'switch.html', {'power': state.power})
    
    def post(self, request):
        state = Switch.objects.get(id=1)
        state.power = not state.power
        state.save()
        return JsonResponse({'power': state.power})