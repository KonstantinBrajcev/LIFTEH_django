import pytest
from django.urls import reverse
from LIFTEH.models import Service, Avr, Work

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
        
        response = client.post(reverse('service_add', args=[test_object.id]), {
            'result': 0,
            'comments': 'Test service comment'
        })
        
        assert response.status_code == 302  # Redirect after success
        assert Service.objects.filter(object=test_object).exists()

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