import pytest
from django.urls import reverse
from LIFTEH.models import Service, Avr, Work
from django.utils import timezone

@pytest.mark.django_db
class TestService:
    def test_service_add_get(self, client, regular_user, test_object):
        """Тест получения формы добавления обслуживания"""
        client.force_login(regular_user)
        response = client.get(reverse('service_add', args=[test_object.id]))
        assert response.status_code == 200
        assert 'service_add.html' in [t.name for t in response.templates]

    def test_service_add_post(self, client, regular_user, test_object):
        """Тест добавления обслуживания"""
        client.force_login(regular_user)
        
        # Попробуем разные варианты данных
        form_data = {
            'object_id': test_object.id,
            'service_date': timezone.now().strftime('%Y-%m-%d'),  # Строковый формат
            'result': '0',  # Строка вместо числа
            'comments': 'Test service comment'
        }
        
        response = client.post(reverse('service_add', args=[test_object.id]), form_data)
        
        print(f"Service add response status: {response.status_code}")
        if response.status_code == 200:
            if hasattr(response, 'context') and 'form' in response.context:
                print("Service form errors:")
                for field, errors in response.context['form'].errors.items():
                    print(f"  {field}: {errors}")
        
        assert response.status_code == 302
        assert Service.objects.filter(object=test_object).exists()

@pytest.mark.django_db
class TestAvr:
    def test_avr_add_get(self, client, regular_user, test_object):
        """Тест получения формы добавления АВР"""
        client.force_login(regular_user)
        response = client.get(reverse('avr_add', args=[test_object.id]))
        assert response.status_code == 200

    def test_avr_add_post(self, client, regular_user, test_object):
        """Тест добавления АВР с работами"""
        client.force_login(regular_user)
        
        response = client.post(reverse('avr_add', args=[test_object.id]), {
            'object': test_object.id,  # Добавляем обязательное поле
            'insert_date': timezone.now().date(),  # Добавляем обязательное поле даты
            'problem': 'Test AVR problem',
            'workname': ['Work 1', 'Work 2'],
            'unit': ['шт', 'м'],
            'quantity': ['2', '5']
        })
        
        assert response.status_code == 302
        avr = Avr.objects.filter(object=test_object).first()
        assert avr is not None
        assert avr.work_set.count() == 2

    def test_avr_edit(self, client, regular_user, test_avr):
        """Тест редактирования АВР"""
        client.force_login(regular_user)
        
        response = client.post(reverse('avr_edit', args=[test_avr.id]), {
            'object': test_avr.object.id,  # Добавляем обязательное поле
            'insert_date': timezone.now().date(),  # Добавляем обязательное поле даты
            'problem': 'Updated problem',
            'result': 1,
            'workname': ['Updated work'],
            'unit': ['шт'],
            'quantity': ['3']
        })
        
        assert response.status_code == 302
        test_avr.refresh_from_db()
        assert test_avr.problem == 'Updated problem'
        assert test_avr.work_set.count() == 1