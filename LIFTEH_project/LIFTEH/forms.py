from datetime import datetime
from .models import Diagnostic
from django import forms
from LIFTEH.models import Object, Avr, Service, Dogovor


class ObjectForm(forms.ModelForm):
    class Meta:
        model = Object
        fields = ['customer', 'address', 'model', 'serial_number', 'work', 'phone', 'name', 'M1',
                  'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10', 'M11', 'M12', 'latitude', 'longitude']
        widgets = {
            'latitude': forms.NumberInput(attrs={
                'step': '0.000001',
                # 'min': '-90',
                # 'max': '90'
            }),
            'longitude': forms.NumberInput(attrs={
                'step': '0.000001',
                # 'min': '-180',
                # 'max': '180'
            }),
        }
    M1 = forms.DecimalField(required=False, decimal_places=2,
                            max_digits=12, widget=forms.NumberInput(attrs={'step': 'any'}))
    M2 = forms.DecimalField(required=False, decimal_places=2,
                            max_digits=12, widget=forms.NumberInput(attrs={'step': 'any'}))
    M3 = forms.DecimalField(required=False, decimal_places=2,
                            max_digits=12, widget=forms.NumberInput(attrs={'step': 'any'}))
    M4 = forms.DecimalField(required=False, decimal_places=2,
                            max_digits=12, widget=forms.NumberInput(attrs={'step': 'any'}))
    M5 = forms.DecimalField(required=False, decimal_places=2,
                            max_digits=12, widget=forms.NumberInput(attrs={'step': 'any'}))
    M6 = forms.DecimalField(required=False, decimal_places=2,
                            max_digits=12, widget=forms.NumberInput(attrs={'step': 'any'}))
    M7 = forms.DecimalField(required=False, decimal_places=2,
                            max_digits=12, widget=forms.NumberInput(attrs={'step': 'any'}))
    M8 = forms.DecimalField(required=False, decimal_places=2,
                            max_digits=12, widget=forms.NumberInput(attrs={'step': 'any'}))
    M9 = forms.DecimalField(required=False, decimal_places=2,
                            max_digits=12, widget=forms.NumberInput(attrs={'step': 'any'}))
    M10 = forms.DecimalField(required=False, decimal_places=2,
                             max_digits=12, widget=forms.NumberInput(attrs={'step': 'any'}))
    M11 = forms.DecimalField(required=False, decimal_places=2,
                             max_digits=12, widget=forms.NumberInput(attrs={'step': 'any'}))
    M12 = forms.DecimalField(required=False, decimal_places=2,
                             max_digits=12, widget=forms.NumberInput(attrs={'step': 'any'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for month in range(1, 13):
            field_name = f'M{month}'
            self.fields[field_name].widget = forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'form-control',
                'type': 'number',
                'lang': 'en'  # Указываем английскую локаль для точки
            })
            self.fields[field_name].localize = True


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['service_date', 'comments', 'result', 'foto']

    def __init__(self, *args, **kwargs):
        self.object_id = kwargs.pop('object_id', None)  # Сохраняем object_id
        super().__init__(*args, **kwargs)

    def save(self, user, commit=True):
        instance = super().save(commit=False)
        instance.user = user  # Добавляем пользователя, который отправил форму
        instance.object_id = self.object_id  # Устанавливаем объект для обслуживания
        if commit:
            instance.save()
        return instance


class AvrForm(forms.ModelForm):
    insert_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Avr
        fields = ['insert_date', 'problem', 'object', 'work_id']


class ObjectAvrForm(forms.Form):
    customer = forms.CharField(max_length=255)
    address = forms.CharField(max_length=255)
    problem = forms.CharField(max_length=500)


# class DiagnosticForm(forms.ModelForm):
#     class Meta:
#         model = Diagnostic
#         fields = ['object', 'end_date', 'result']
#         widgets = {
#             'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#         }

class DiagnosticForm(forms.ModelForm):
    customer = forms.CharField(max_length=255, label='Заказчик')
    address = forms.CharField(max_length=255, label='Адрес')
    phone = forms.CharField(max_length=20, label='Телефон')
    name = forms.CharField(max_length=255, label='Имя')

    class Meta:
        model = Diagnostic
        fields = ['end_date', 'fact_date', 'result']
        widgets = {
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fact_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем проверку на существование object, так как при создании его нет
        if self.instance.pk and hasattr(self.instance, 'object'):
            self.fields['customer'].initial = self.instance.object.customer
            self.fields['address'].initial = self.instance.object.address
            self.fields['phone'].initial = self.instance.object.phone
            self.fields['name'].initial = self.instance.object.name

    def save(self, commit=True):
        diagnostic = super().save(commit=False)

        # Создаем или обновляем объект
        if hasattr(diagnostic, 'object') and diagnostic.object:
            # Обновляем существующий объект
            obj = diagnostic.object
            obj.customer = self.cleaned_data['customer']
            obj.address = self.cleaned_data['address']
            obj.phone = self.cleaned_data['phone']
            obj.name = self.cleaned_data['name']
            obj.save()
        else:
            # Создаем новый объект
            obj = Object(
                customer=self.cleaned_data['customer'],
                address=self.cleaned_data['address'],
                phone=self.cleaned_data['phone'],
                name=self.cleaned_data['name']
            )
            obj.save()
            diagnostic.object = obj

        if commit:
            diagnostic.save()
        return diagnostic


class DogovorForm(forms.ModelForm):
    class Meta:
        model = Dogovor
        fields = ['number', 'customer', 'date',
                  'financing', 'longtime', 'is_active']
        widgets = {
            'date': forms.DateInput(
                format='%Y-%m-%d',  # Важно: формат для HTML5 date input
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }
            ),
            'number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Пример: ДГ-2024-001'
            }),
            'customer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Полное наименование заказчика'
            }),
            'financing': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'number': 'Номер договора',
            'customer': 'Заказчик',
            'date': 'Дата договора',
            'financing': 'Тип финансирования',
            'longtime': 'Долгосрочный договор',
            'is_active': 'Активный договор',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # Если это создание нового
            from datetime import datetime
            self.fields['date'].initial = datetime.now().date()
            self.fields['number'].initial = f"{datetime.now().strftime('%Y%m%d')}"
            self.fields['is_active'].initial = True
            self.fields['longtime'].initial = False
