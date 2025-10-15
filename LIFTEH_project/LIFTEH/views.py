from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
import requests
import re
import json
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views import View
from django.db import models, connection
from django.db.models import Sum, FloatField, F, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import TemplateView
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from LIFTEH.models import Object, Avr, Service, Work, Diagnostic, Problem, Object, AccessUser  
from LIFTEH.forms import ObjectForm, ServiceForm, AvrForm, ObjectAvrForm, DiagnosticForm


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


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
        current_month = datetime.now().month
        month = int(self.request.GET.get('month', current_month))
        year = timezone.now().year

        # Исправляем обработку города (None → пустая строка)
        selected_city = self.request.GET.get('city', '')
        if selected_city == 'None':
            selected_city = ''

        selected_colors = self.request.GET.getlist('colors', ['all'])

        # Если выбран "Все цвета" или ничего не выбрано, показываем все варианты
        if 'all' in selected_colors or not selected_colors:
            selected_colors = ['green', 'yellow', 'red', 'gray']

        # НОВАЯ ЛОГИКА ДОСТУПА К ОБЪЕКТАМ
        # Проверяем, есть ли у пользователя записи в AccessUser
        has_access_entries = AccessUser.objects.filter(user=self.request.user).exists()
        
        # Базовый запрос с фильтрацией по месяцу
        if self.request.user.is_superuser or not has_access_entries:
            # Суперпользователь ИЛИ пользователь без записей в AccessUser видят ВСЕ объекты
            objects = Object.objects.filter(**{f'M{month}__gt': 0})
            print(f"User {self.request.user.username} sees ALL objects (superuser: {self.request.user.is_superuser}, has_access_entries: {has_access_entries})")
        else:
            # Пользователь с записями в AccessUser видит только свои объекты
            objects = Object.objects.filter(
                accessuser__user=self.request.user,
                **{f'M{month}__gt': 0}
            ).distinct()
            print(f"User {self.request.user.username} sees ONLY assigned objects (has_access_entries: {has_access_entries})")

        # Фильтрация по городу (только если город выбран)
        if selected_city:
            objects = objects.filter(address__icontains=selected_city)

        # Собираем информацию о цветах
        service_records = {}
        color_mapping = {'green': 0, 'yellow': 1, 'red': 2, 'gray': None}

        for obj in objects:
            service_records[obj.id] = obj.service_set.filter(
                service_date__year=year,
                service_date__month=month
            ).last()

        # Фильтрация по цветам (исправленная логика)
        filtered_objects = []

        for obj in objects:
            service_record = service_records.get(obj.id)

            # Для серого цвета (отсутствие записи)
            if 'gray' in selected_colors and service_record is None:
                filtered_objects.append(obj)
            # Для других цветов (наличие записи с нужным результатом)
            elif service_record and any(
                color in selected_colors
                and service_record.result == color_mapping.get(color)
                for color in ['green', 'yellow', 'red']
            ):
                filtered_objects.append(obj)

        # НОВАЯ ЛОГИКА ДОСТУПА К ЗАДАЧАМ
        if self.request.user.is_superuser or not has_access_entries:
            # Суперпользователь ИЛИ пользователь без записей в AccessUser видят ВСЕ задачи
            problems = Problem.objects.all().order_by('-created_date')
        else:
            # Пользователь с записями в AccessUser видит только свои задачи
            problems = Problem.objects.filter(user=self.request.user).order_by('-created_date')

        context.update({
            'month': month,
            'current_month': current_month,
            'objects': filtered_objects,
            'service_records': service_records,
            'cities': sorted({re.match(r'^(г\.п\.|ж/д ст\.|г\.|п\.|д\.)\s*[^,]+', obj.address).group(0).strip()
                              for obj in Object.objects.all()
                              if re.match(r'^(г\.п\.|ж/д ст\.|г\.|п\.|д\.)\s*[^,]+', obj.address)}),
            'selected_city': selected_city,
            'selected_colors': selected_colors,
            'avrs': Avr.objects.filter(Q(result__isnull=True) | Q(result__in=[0, 1, 2])),
            'problems': problems
        })

        # Добавляем контекст из других представлений
        charts_view = ChartsView()
        charts_view.request = self.request
        context.update(charts_view.get_context_data())

        tasks_view = TasksView()
        tasks_view.request = self.request
        context.update(tasks_view.get_context_data())

        diagnostic_view = DiagnosticView()
        diagnostic_view.request = self.request
        context.update(diagnostic_view.get_context_data())

        return context


# ----------- ЗАДАЧИ -----------
class TasksView(AdminRequiredMixin, TemplateView):
    template_name = 'tasks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            now = timezone.localtime(timezone.now())
            current_month = now.month
            first_day = timezone.make_aware(
                timezone.datetime(now.year, now.month, 1))
            last_day = timezone.make_aware(timezone.datetime(
                now.year + 1, 1, 1) if now.month == 12 else
                timezone.datetime(now.year, now.month + 1, 1)
            )

            # 1. Объекты, которые должны обслуживаться в текущем месяце
            # но еще не обслужены
            month_column = f"M{current_month}"

            # Получаем объекты, которые должны обслуживаться в текущем месяце
            objects_to_service = Object.objects.filter(
                **{month_column + '__gt': 0})

            # Получаем ID объектов, которые уже обслужены в этом месяце
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT object_id
                    FROM lifteh_service
                    WHERE service_date >= %s AND service_date < %s
                """, [first_day, last_day])
                serviced_ids = [row[0] for row in cursor.fetchall()]

            # Исключаем уже обслуженные объекты
            objects_without_service = list(
                objects_to_service.exclude(id__in=serviced_ids).values()
            )

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
                    WHERE a.result = 1
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


# --------ДИАГНОСТИКА -----------

class DiagnosticView(TemplateView):
    template_name = 'diagnostic.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['diagnostics'] = Diagnostic.objects.filter(
            fact_date__isnull=True
        ).select_related('object')
        return context


def diagnostic_add(request):
    if request.method == 'POST':
        form = DiagnosticForm(request.POST)
        if form.is_valid():
            diagnostic = form.save(commit=False)
            diagnostic.insert_date = timezone.now()
            diagnostic.user = request.user
            diagnostic.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect(reverse('to') + '#diagnostic')
    else:
        form = DiagnosticForm()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'diagnostic_add.html', {'form': form})
    return render(request, 'diagnostic_add.html', {'form': form})


def diagnostic_edit(request, pk):
    diagnostic = get_object_or_404(Diagnostic, pk=pk)
    if request.method == 'POST':
        form = DiagnosticForm(request.POST, instance=diagnostic)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect(reverse('to') + '#diagnostic')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render(request, 'diagnostic_edit.html', {
                    'form': form,
                    'diagnostic': diagnostic
                }, status=400)
    else:
        form = DiagnosticForm(instance=diagnostic)

    return render(request, 'diagnostic_edit.html', {
        'form': form,
        'diagnostic': diagnostic
    })


def diagnostic_delete(request, pk):
    diagnostic = get_object_or_404(Diagnostic, pk=pk)
    if request.method == 'POST':
        diagnostic.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        messages.success(request, 'Диагностика успешно удалена')
        return redirect(reverse('to') + '#diagnostic')
    return redirect(reverse('to') + '#diagnostic')


# ------ РАБОТА С ОБЪЕКТАМИ ------

def objects_edit(request, pk):
    servicing = get_object_or_404(Object, pk=pk)
    if request.method == "POST":
        form = ObjectForm(request.POST, instance=servicing)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect(reverse('to') + '#service')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render(request, 'object_edit.html', {'form': form, 'object': servicing}, status=400)

    form = ObjectForm(instance=servicing)
    return render(request, 'object_edit.html', {'form': form, 'object': servicing})


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
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect(reverse('to') + '#service')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Invalid method'})
    return redirect(reverse('to') + '#service')


@login_required
def object_table_view(request):
    # Для суперпользователя - все объекты
    if request.user.is_superuser:
        objects = Object.objects.all()
    else:
        # Для обычных пользователей - только объекты из таблицы доступа
        objects = Object.objects.filter(
            accessuser__user=request.user
        ).distinct()
    
    # Ваш существующий код для service_records и другого контекста
    service_records = {}  # Ваша логика для service_records
    
    context = {
        'objects': objects,
        'service_records': service_records,
    }
    
    return render(request, 'object_table.html', context)

# ------ РАБОТА С АВР ------

@login_required
def avr_add(request, pk):
    current_datetime = timezone.now()
    obj = get_object_or_404(Object, id=pk)

    if request.method == 'POST':
        form = AvrForm(request.POST)

        if form.is_valid():
            avr = form.save(commit=False)
            avr.user = request.user
            avr.object = obj
            avr.save()

            # Получаем списки значений
            worknames = request.POST.getlist('workname')
            units = request.POST.getlist('unit')
            quantities = request.POST.getlist('quantity')

            # Проверяем, что все списки одинаковой длины
            if len(worknames) == len(units) == len(quantities):
                works = []
                for i in range(len(worknames)):
                    if worknames[i].strip():  # Проверяем, что название не пустое
                        works.append(Work(
                            avr=avr,
                            name=worknames[i],
                            unit=units[i],
                            quantity=int(quantities[i])
                        ))

                if works:  # Если есть хотя бы одна работа
                    Work.objects.bulk_create(works)

            return redirect(reverse('to') + '#acts')
        else:
            print("Ошибки формы:", form.errors)
    else:
        form = AvrForm()

    return render(request, 'avr_add.html', {
        'form': form,
        'object': obj,
        'current_datetime': current_datetime
    })


def avr_edit(request, pk):
    avr = get_object_or_404(Avr, pk=pk)
    current_datetime = timezone.now()

    if request.method == 'POST':
        # Обновляем основную информацию AVR
        avr.problem = request.POST.get('problem', '')
        # avr.work_id = request.POST.get('work_id', None)
        avr.work_id = request.POST.get('work_id', 0) or None
        # Сохраняем результат (значение radio)
        avr.result = request.POST.get('result')
        avr.save()

        # Удаляем все старые работы
        avr.work_set.all().delete()

        # Сохраняем новые работы
        worknames = request.POST.getlist('workname')
        units = request.POST.getlist('unit')
        quantities = request.POST.getlist('quantity')

        works = []
        for workname, unit, quantity in zip(worknames, units, quantities):
            if workname.strip():  # Проверяем, что название работы не пустое
                works.append(Work(
                    avr=avr,
                    name=workname,
                    unit=unit,
                    quantity=quantity
                ))

        Work.objects.bulk_create(works)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('to') + '#acts'
            })
        return redirect(reverse('to') + '#acts')

    return render(request, 'avr_edit.html', {
        'avr': avr,
        'current_datetime': current_datetime
    })


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
                insert_date=timezone.now(),
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
    # services = Service.objects.filter(object=obj)
    services = Service.objects.filter(object=obj).order_by('-service_date')[:2]
    current_datetime = timezone.now()

    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, object_id=object_id)
        if form.is_valid():
            form.save(user=request.user)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect(reverse('to') + '#service')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render(request, 'service_add.html', {
                    'form': form,
                    'object': obj,
                    'services': services,
                    'current_datetime': current_datetime
                }, status=400)
            return HttpResponse("Форма невалидна!")

    form = ServiceForm()
    return render(request, 'service_add.html', {
        'form': form,
        'object': obj,
        'services': services,
        'current_datetime': current_datetime
    })


# ---------- ГРАФИКИ ------------
class ChartsView(AdminRequiredMixin, TemplateView):
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
                    if month_value is not None and float(month_value) > 0:
                        total_sum += float(month_value)
                        total_non_null_months += 1

            # Рассчитываем среднее значение (избегаем деления на 0)
            # Исключаем заказчиков, у которых все значения NULL или 0
            if total_non_null_months > 0:
                avg_value = total_sum / total_non_null_months

                # Добавляем только если среднее значение больше 0
                if avg_value > 0:
                    customers_avg.append({
                        'customer': customer_name,
                        # Округляем до 2 знаков
                        'avg_value': round(avg_value, 2)
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



# --------- РАБОТА С ПРОБЛЕМАМИ ----------
def problems_view(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # НОВАЯ ЛОГИКА ДОСТУПА К ЗАДАЧАМ
    # Проверяем, есть ли у пользователя записи в AccessUser
    has_access_entries = AccessUser.objects.filter(user=request.user).exists()
    
    if request.user.is_superuser or not has_access_entries:
        # Суперпользователь ИЛИ пользователь без записей в AccessUser видят ВСЕ задачи
        problems = Problem.objects.all().order_by('-created_date')
        print(f"User {request.user.username} sees ALL problems (superuser: {request.user.is_superuser}, has_access_entries: {has_access_entries})")
    else:
        # Пользователь с записями в AccessUser видит только свои задачи
        problems = Problem.objects.filter(user=request.user).order_by('-created_date')
        print(f"User {request.user.username} sees ONLY assigned problems (has_access_entries: {has_access_entries})")
    
    today = timezone.now().date()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'problems_table.html', {
            'problems': problems,
            'today': today
        })

    return render(request, 'problems.html', {
        'problems': problems,
        'today': today
    })


def add_problem(request):
    print(f"Add problem called. Method: {request.method}")
    print(f"Headers: {dict(request.headers)}")

    if request.method == 'POST':
        # Обработка отправки формы
        name = request.POST.get('name')
        print(f"Received name: '{name}'")

        if name and name.strip():
            problem = Problem.objects.create(
                name=name.strip(),
                created_date=timezone.now().date(),
                user=request.user  # Добавляем текущего пользователя
            )
            print(f"Created problem: {problem.id} - {problem.name} - User: {problem.user.username}")

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                print("Returning JSON success response")
                return JsonResponse({'success': True})
            else:
                return redirect(reverse('to') + '#problems')
        else:
            print("Name is empty or invalid")

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                print("Returning JSON error response")
                return JsonResponse({'success': False, 'error': 'Неверные данные: название задачи не может быть пустым'})

    elif request.method == 'GET':
        # Показать форму (для AJAX запроса)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            print("Returning form HTML")
            return render(request, 'problems_form.html')

    # Для не-AJAX запросов или ошибок
    return redirect(reverse('to') + '#problems')

@require_POST
def update_problem_status(request, problem_id):
    try:
        # Логируем входящий запрос
        print(f"Incoming request: {request.method} {request.path}")
        print(f"Request body: {request.body}")

        # Проверяем, что это JSON-запрос
        if request.content_type != 'application/json':
            return JsonResponse(
                {'success': False, 'error': 'Content-Type must be application/json'},
                status=400
            )

        # Парсим JSON
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse(
                {'success': False, 'error': f'Invalid JSON: {str(e)}'},
                status=400
            )

        # Получаем задачу
        problem = Problem.objects.get(id=problem_id)
        problem.is_completed = data.get('is_completed', False)
        problem.save()

        return JsonResponse({
            'success': True,
            'is_completed': problem.is_completed
        })

    except Problem.DoesNotExist:
        return JsonResponse(
            {'success': False, 'error': 'Problem not found'},
            status=404
        )
    except Exception as e:
        return JsonResponse(
            {'success': False, 'error': str(e)},
            status=500
        )



def edit_problem(request, problem_id):
    print(f"Edit problem called. ID: {problem_id}, Method: {request.method}")
    
    User = get_user_model()  # Получаем модель пользователя

    try:
        problem = Problem.objects.get(id=problem_id)
        
        # Проверка прав доступа
        if not request.user.is_superuser and problem.user != request.user:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'У вас нет прав для редактирования этой задачи'}, status=403)
            return redirect(reverse('to') + '#problems')
            
    except Problem.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Задача не найдена'})
        return redirect(reverse('to') + '#problems')

    if request.method == 'POST':
        # Обработка сохранения изменений
        name = request.POST.get('name')
        created_date = request.POST.get('created_date')
        user_id = request.POST.get('user_id')

        print(f"Received data - name: '{name}', date: '{created_date}', user_id: '{user_id}'")

        if name and name.strip() and created_date:
            problem.name = name.strip()
            try:
                problem.created_date = created_date
                
                # Обновляем пользователя, если это суперпользователь
                if request.user.is_superuser and user_id:
                    try:
                        new_user = User.objects.get(id=user_id)
                        problem.user = new_user
                        print(f"Changed user to: {new_user.username}")
                    except User.DoesNotExist:
                        print(f"User with id {user_id} not found")
                
                problem.save()

                print(f"Updated problem: {problem.id} - {problem.name} - User: {problem.user.username}")

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True})
                else:
                    return redirect(reverse('to') + '#problems')

            except ValueError as e:
                print(f"Invalid date format: {e}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Неверный формат даты'})
        else:
            print("Invalid data received")

    elif request.method == 'GET':
        # Показать форму редактирования
        print(f"Returning edit form for problem {problem_id}")
        
        # Получаем список пользователей для выпадающего списка (только для суперпользователей)
        users = User.objects.all().order_by('username') if request.user.is_superuser else []
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return render(request, 'edit_problem_form.html', {
                'problem': problem,
                'users': users
            })
        else:
            return render(request, 'edit_problem_form.html', {
                'problem': problem,
                'users': users
            })

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Неверные данные'})

    return redirect(reverse('to') + '#problems')


@require_POST
def delete_problem(request, problem_id):
    print(f"Delete problem called. ID: {problem_id}, Method: {request.method}")

    if request.method == 'POST':
        try:
            problem = Problem.objects.get(id=problem_id)
            
            # Проверка прав доступа
            if not request.user.is_superuser and problem.user != request.user:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'У вас нет прав для удаления этой задачи'}, status=403)
                return redirect(reverse('to') + '#problems')
            
            problem_name = problem.name
            problem.delete()
            print(f"Deleted problem: {problem_id} - {problem_name}")

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Задача удалена'})
            else:
                return redirect(reverse('to') + '#problems')

        except Problem.DoesNotExist:
            print(f"Problem {problem_id} not found")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Задача не найдена'})

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})

    return redirect(reverse('to') + '#problems')



# ---------- ЭТО API для FLUTTER --------------
# Добавьте эти импорты
class ApiLoginView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def _add_cors_headers(self, response):
        """Добавляет CORS headers к response"""
        origin = self.request.META.get('HTTP_ORIGIN', '')

        # Разрешаем все локальные origin для разработки
        if settings.DEBUG and origin:
            response["Access-Control-Allow-Origin"] = origin
        else:
            response["Access-Control-Allow-Origin"] = "*"

        response["Access-Control-Allow-Methods"] = "POST, OPTIONS, GET"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        response["Access-Control-Allow-Credentials"] = "true"
        return response

    def options(self, request, *args, **kwargs):
        response = JsonResponse({})
        return self._add_cors_headers(response)

    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                response_data = {
                    'success': True,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'is_superuser': user.is_superuser
                    }
                }
                response = JsonResponse(response_data)
            else:
                response_data = {
                    'success': False,
                    'error': 'Неверный логин или пароль'
                }
                response = JsonResponse(response_data, status=401)

            return self._add_cors_headers(response)

        except Exception as e:
            response = JsonResponse({
                'success': False,
                'error': f'Ошибка сервера: {str(e)}'
            }, status=500)
            return self._add_cors_headers(response)



# ------РАБОТА С КАРТАМИ----------
@login_required
def get_objects(request):
    """API endpoint для получения объектов с координатами"""
    try:
        # Получаем параметр фильтра из запроса
        filter_type = request.GET.get('filter', 'all')
        current_month = timezone.now().month
        current_year = timezone.now().year

        # НОВАЯ ЛОГИКА ДОСТУПА К ОБЪЕКТАМ (как в ToView)
        # Проверяем, есть ли у пользователя записи в AccessUser
        has_access_entries = AccessUser.objects.filter(user=request.user).exists()
        
        # Базовый запрос объектов с координатами
        if request.user.is_superuser or not has_access_entries:
            # Суперпользователь ИЛИ пользователь без записей в AccessUser видят ВСЕ объекты
            objects = Object.objects.exclude(
                latitude__isnull=True).exclude(longitude__isnull=True)
            print(f"Map: User {request.user.username} sees ALL objects (superuser: {request.user.is_superuser}, has_access_entries: {has_access_entries})")
        else:
            # Пользователь с записями в AccessUser видит только свои объекты
            objects = Object.objects.filter(
                accessuser__user=request.user
            ).exclude(
                latitude__isnull=True
            ).exclude(
                longitude__isnull=True
            ).distinct()
            print(f"Map: User {request.user.username} sees ONLY assigned objects (has_access_entries: {has_access_entries})")

        # Фильтрация по типу (если нужна)
        if filter_type == 'without_marks':
            # Объекты без записей осмотра в текущем месяце
            objects_with_service = Service.objects.filter(
                service_date__year=current_year,
                service_date__month=current_month
            ).values_list('object_id', flat=True)

            objects = objects.exclude(id__in=objects_with_service)

        objects_data = []
        for obj in objects:
            manual_url = f"https://disk.yandex.ru/d/{obj.folder_id}" if obj.folder_id else None

            # Получаем последний осмотр для этого объекта
            last_service = Service.objects.filter(
                object=obj).order_by('-service_date').first()

            objects_data.append({
                'id': obj.id,
                'customer': obj.customer,
                'address': obj.address,
                'latitude': float(obj.latitude) if obj.latitude else None,
                'longitude': float(obj.longitude) if obj.longitude else None,
                'model': obj.model,
                'phone': obj.phone,
                'manual_url': manual_url,
                'last_service_date': last_service.service_date.strftime('%d.%m.%Y') if last_service else None,
                'last_service_comments': last_service.comments if last_service else None,
                # Добавляем информацию о доступе для отладки
                'has_access': True  # Все объекты в этом списке уже отфильтрованы по правам доступа
            })

        print(f"Map: Returning {len(objects_data)} objects for user {request.user.username}")
        return JsonResponse(objects_data, safe=False)

    except Exception as e:
        print(f"Map error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)



@login_required
def map_view(request):
    """Представление для отображения карты с данными в шаблоне"""
    
    # Передаем информацию о правах доступа в шаблон (для возможного использования)
    has_access_entries = AccessUser.objects.filter(user=request.user).exists()
    
    context = {
        'objects_data': '[]',  # Данные загружаются через API
        'YANDEX_MAPS_API_KEY': settings.YANDEX_MAPS_API_KEY,
        'has_access_entries': has_access_entries,  # Для возможного использования в шаблоне
        'user_is_superuser': request.user.is_superuser  # Для возможного использования в шаблоне
    }
    return render(request, 'map.html', context)



# ------ API ТРЕКЕРОВ --------
@login_required
def get_tracker_locations(request):
    """API endpoint для получения текущих координат трекеров"""
    try:
        # ПРОВЕРКА ПРАВ ДОСТУПА - как в других функциях
        has_access_entries = AccessUser.objects.filter(user=request.user).exists()
        
        # Если пользователь имеет ограниченные права (есть записи в AccessUser), не показываем автомобили
        if not request.user.is_superuser and has_access_entries:
            print(f"Map: User {request.user.username} has limited access - hiding transport")
            return JsonResponse([], safe=False)  # Возвращаем пустой список
        
        # Авторизация в API
        auth_url = "http://monitoring.truck-control.info/api/login"
        auth_data = {
            "login": settings.TRACKER_API_LOGIN,
            "password": settings.TRACKER_API_PASSWORD
        }

        # Получаем токен
        auth_response = requests.post(auth_url, json=auth_data)
        if auth_response.status_code != 200:
            return JsonResponse({'error': 'Ошибка авторизации в API'}, status=500)

        auth_result = auth_response.json()
        if auth_result.get('status') != 'ok':
            return JsonResponse({'error': 'Неверные учетные данные API'}, status=500)

        token = auth_result['data']['token']

        # Получаем данные трекеров
        tracker_url = f"http://monitoring.truck-control.info/api/get_last_data?token={token}"
        tracker_response = requests.post(tracker_url)

        if tracker_response.status_code != 200:
            return JsonResponse({'error': 'Ошибка получения данных трекеров'}, status=500)

        tracker_data = tracker_response.json()

        # Форматируем данные для карты
        formatted_trackers = []
        for tracker in tracker_data:
            if tracker.get('valid') == 1 and tracker.get('xcoord') and tracker.get('ycoord'):
                formatted_trackers.append({
                    'tracker_id': tracker.get('trackerid'),
                    'car_id': tracker.get('CarID', f"Трекер {tracker.get('trackerid')}"),
                    'driver_name': tracker.get('DriverName'),
                    'latitude': float(tracker['xcoord']),
                    'longitude': float(tracker['ycoord']),
                    'speed': tracker.get('speed', 0),
                    'satellites': tracker.get('satcount', 0),
                    'last_update': datetime.fromtimestamp(tracker.get('unixtime_coord', 0)).strftime('%d.%m.%Y %H:%M:%S'),
                    'mileage': round(tracker.get('milage_db', 0), 2)
                })

        print(f"Map: Returning {len(formatted_trackers)} trackers for user {request.user.username}")
        return JsonResponse(formatted_trackers, safe=False)

    except Exception as e:
        print(f"Map tracker error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
