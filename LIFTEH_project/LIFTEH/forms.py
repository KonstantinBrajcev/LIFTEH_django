<<<<<<< HEAD
from django import forms
from LIFTEH.models import Object, Avr, Service


class ObjectForm(forms.ModelForm):
    class Meta:
        model = Object
        fields = ['customer', 'address', 'model', 'work', 'phone', 'name', 'M1',
                  'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10', 'M11', 'M12']
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
    # insert_date = forms.DateTimeField(
    #     widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    #     input_formats=['%Y-%m-%dT%H:%M']
    # )
=======
from .models import Diagnostic
from django import forms
from LIFTEH.models import Object, Avr, Service


class ObjectForm(forms.ModelForm):
    class Meta:
        model = Object
        fields = ['customer', 'address', 'model', 'work', 'phone', 'name', 'M1',
                  'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10', 'M11', 'M12']
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


class DiagnosticForm(forms.ModelForm):
    class Meta:
        model = Diagnostic
        fields = ['object', 'end_date', 'result']
        widgets = {
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
>>>>>>> bubuka
