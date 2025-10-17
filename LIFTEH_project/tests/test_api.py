import pytest
import json
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class TestApiLogin:
    def test_api_login_success(self, client, regular_user):
        """Тест успешного API логина"""
        response = client.post(
            reverse('api_login'),
            data=json.dumps({
                'username': 'testuser',
                'password': 'testpass123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert data['user']['username'] == 'testuser'

    def test_api_login_failure(self, client):
        """Тест неудачного API логина"""
        response = client.post(
            reverse('api_login'),
            data=json.dumps({
                'username': 'wrong',
                'password': 'wrong'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data['success'] == False

    def test_api_login_options(self, client):
        """Тест CORS OPTIONS запроса"""
        response = client.options(reverse('api_login'))
        assert response.status_code == 200
        assert 'Access-Control-Allow-Origin' in response

class TestMapAPI:
    def test_get_objects_api(self, client, regular_user, test_object):
        """Тест API получения объектов для карты"""
        client.force_login(regular_user)
        
        response = client.get(reverse('get_objects'))
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]['customer'] == 'Test Customer'
        assert data[0]['latitude'] == 55.7558

    def test_get_tracker_locations(self, client, regular_user):
        """Тест API получения местоположения трекеров"""
        client.force_login(regular_user)
        
        response = client.get(reverse('get_tracker_locations'))
        # Может возвращать ошибку или пустой список в зависимости от настроек
        assert response.status_code == 200

    def test_map_view(self, client, regular_user):
        """Тест отображения карты"""
        client.force_login(regular_user)
        
        response = client.get(reverse('map'))
        assert response.status_code == 200
        assert 'map.html' in [t.name for t in response.templates]