from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.http import HttpResponse
from django.views.generic import TemplateView, ListView, CreateView
from django.views import View
from django.db import models, connection
from django.db.models import Sum, FloatField, F, Q
from django.db.models.functions import Coalesce
from django.utils.timezone import now
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import TemplateView
import re
import json
from django.http import JsonResponse
from django.template.loader import render_to_string
from LIFTEH.models import Object, Avr, Service, Work, Diagnostic, Switch, Problem
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
        # Получаем параметры фильтрации из GET-запроса
        month = self.request.GET.get('month', timezone.now().month)
        year = timezone.now().year
        selected_city = self.request.GET.get('city')
        selected_colors = self.request.GET.getlist('colors')

        # Удаляем пустые значения из списка выбранных цветов
        selected_colors = [color for color in selected_colors if color]

        objects = Object.objects.all()
        objects = objects.filter(
            **{f'M{month}__isnull': False}).exclude(**{f'M{month}': 0})

        # Извлекаем города
        city_set = set()
        for obj in objects:
            match = re.match(
                r'^(г\.п\.|ж/д ст\.|г\.|п\.|д\.)\s*[^,]+', obj.address)
            if match:
                city_set.add(match.group(0).strip())

        # Фильтрация по городу
        if selected_city:
            objects = objects.filter(address__icontains=selected_city)

        # Собираем информацию о цветах
        service_records = {}
        color_mapping = {
            'green': 0,
            'yellow': 1,
            'red': 2,
            'gray': None
        }

        for obj in objects:
            service_record = obj.service_set.filter(
                service_date__year=year,
                service_date__month=month
            ).last()
            service_records[obj.id] = service_record

        # Фильтрация по выбранным цветам
        if selected_colors:
            filtered_objects = []
            # allowed_results = [color_mapping[color] for color in selected_colors]
            allowed_results = [color_mapping[color] for color in selected_colors if color in color_mapping]

            for obj in objects:
                service_record = service_records.get(obj.id)
                if 'gray' in selected_colors and service_record is None:
                    filtered_objects.append(obj)
                elif service_record and service_record.result in allowed_results:
                    filtered_objects.append(obj)

            objects = filtered_objects
        
        avrs = Avr.objects.filter(
            Q(result__isnull=True) | Q(result__in=[0, 1, 2])
        )

        context.update({
            'month': month,
            'objects': objects,
            'service_records': service_records,
            'cities': sorted(city_set),
            'selected_city': selected_city,
            'selected_colors': selected_colors,
            # 'avrs': Avr.objects.all()
            'avrs': avrs
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
    problems = Problem.objects.all().order_by('-created_date')
    today = timezone.now().date()
    return render(request, 'problems.html', {
        'problems': problems,
        'today': today
    })

def add_problem(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        # created_date = request.POST.get('created_date')
        Problem.objects.create(name=name, created_date=timezone.now().date())
    return redirect('problems')

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
    
@require_POST
def edit_problem(request, problem_id):
    try:
        problem = Problem.objects.get(id=problem_id)
        problem.name = request.POST.get('name')
        # problem.created_date = request.POST.get('created_date')
        problem.save()
        return JsonResponse({'success': True})
    except Problem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Problem not found'}, status=404)

@require_POST
def delete_problem(request, problem_id):
    try:
        problem = Problem.objects.get(id=problem_id)
        problem.delete()
        return JsonResponse({'success': True})
    except Problem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Problem not found'}, status=404)