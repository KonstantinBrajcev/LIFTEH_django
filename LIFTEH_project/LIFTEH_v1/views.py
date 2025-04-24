from django.utils import timezone
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views import View
import re
from django.utils.timezone import now
from LIFTEH.models import Object, Avr, Service
from LIFTEH.forms import ObjectForm, ServiceForm, AvrForm, ObjectAvrForm


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
