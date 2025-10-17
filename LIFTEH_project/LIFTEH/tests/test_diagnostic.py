import pytest
from django.urls import reverse
from LIFTEH.models import Diagnostic

class TestDiagnostic:
    def test_diagnostic_view(self, client, regular_user):
        """Тест отображения диагностики"""
        client.force_login(regular_user)
        response = client.get(reverse('to') + '#diagnostic')
        assert response.status_code == 200

    def test_diagnostic_add(self, client, regular_user, test_object):
        """Тест добавления диагностики"""
        client.force_login(regular_user)
        
        response = client.post(reverse('diagnostic_add'), {
            'object': test_object.id,
            'problem': 'Test diagnostic problem'
        })
        
        assert response.status_code == 302
        assert Diagnostic.objects.filter(object=test_object).exists()

    def test_diagnostic_edit(self, client, regular_user, test_object):
        """Тест редактирования диагностики"""
        diagnostic = Diagnostic.objects.create(
            object=test_object,
            user=regular_user,
            problem='Original problem'
        )
        
        client.force_login(regular_user)
        response = client.post(reverse('diagnostic_edit', args=[diagnostic.id]), {
            'object': test_object.id,
            'problem': 'Updated problem'
        })
        
        assert response.status_code == 302
        diagnostic.refresh_from_db()
        assert diagnostic.problem == 'Updated problem'