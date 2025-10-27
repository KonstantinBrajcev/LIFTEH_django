import pytest
import json
from datetime import datetime
from django.test import Client, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from LIFTEH.models import Object, AccessUser, Service, Avr, Problem, Diagnostic

User = get_user_model()

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def factory():
    return RequestFactory()

@pytest.fixture
@pytest.mark.django_db
def regular_user():
    user = User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )
    return user

@pytest.fixture
@pytest.mark.django_db
def admin_user():
    user = User.objects.create_superuser(
        username='admin',
        password='adminpass123',
        email='admin@example.com'
    )
    return user

@pytest.fixture
@pytest.mark.django_db
def test_object():
    current_month = datetime.now().month
    object_data = {
        'customer': 'Test Customer',
        'address': 'г. Москва, ул. Тестовая, 1',
        'model': 'Test Model',
        'phone': '+79999999999',
        'latitude': 55.7558,
        'longitude': 37.6173,
    }
    
    # Добавляем данные для текущего месяца
    object_data[f'M{current_month}'] = 150.0
    
    return Object.objects.create(**object_data)

@pytest.fixture
@pytest.mark.django_db
def test_service(test_object, regular_user):
    return Service.objects.create(
        object=test_object,
        user=regular_user,
        result=0,  # green
        comments='Test service comment'
    )

@pytest.fixture
@pytest.mark.django_db
def test_avr(test_object, regular_user):
    return Avr.objects.create(
        object=test_object,
        user=regular_user,
        problem='Test problem'
    )

@pytest.fixture
@pytest.mark.django_db
def test_problem(regular_user):
    return Problem.objects.create(
        name='Test problem',
        user=regular_user
    )

@pytest.fixture
@pytest.mark.django_db
def test_access_user(test_object, regular_user):
    return AccessUser.objects.create(
        user=regular_user,
        object=test_object
    )