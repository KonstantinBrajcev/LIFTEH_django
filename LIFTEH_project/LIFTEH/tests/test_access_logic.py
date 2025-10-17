import pytest
from django.urls import reverse
from LIFTEH.models import Object, AccessUser

class TestObjectAccessLogic:
    def test_superuser_sees_all_objects(self, client, admin_user, test_object):
        """Суперпользователь видит все объекты"""
        client.force_login(admin_user)
        
        # Создаем второй объект
        Object.objects.create(
            customer='Another Customer',
            address='г. СПб, ул. Другая, 2',
            M1=200.0
        )
        
        response = client.get(reverse('to'))
        objects_in_context = list(response.context['objects'])
        
        # Суперпользователь должен видеть все 2 объекта
        assert len(objects_in_context) == 2

    def test_regular_user_without_access_sees_all(self, client, regular_user, test_object):
        """Обычный пользователь без записей в AccessUser видит все объекты"""
        client.force_login(regular_user)
        
        response = client.get(reverse('to'))
        objects_in_context = list(response.context['objects'])
        
        assert len(objects_in_context) == 1
        assert objects_in_context[0].customer == 'Test Customer'

    def test_regular_user_with_access_sees_only_assigned(self, client, regular_user, test_object, test_access_user):
        """Пользователь с записями в AccessUser видит только свои объекты"""
        client.force_login(regular_user)
        
        # Создаем второй объект, но не даем к нему доступ
        Object.objects.create(
            customer='Another Customer',
            address='г. СПб, ул. Другая, 2',
            M1=200.0
        )
        
        response = client.get(reverse('to'))
        objects_in_context = list(response.context['objects'])
        
        # Должен видеть только один объект, к которому есть доступ
        assert len(objects_in_context) == 1
        assert objects_in_context[0].customer == 'Test Customer'

    def test_object_filtering_by_city(self, client, regular_user):
        """Тестирование фильтрации объектов по городу"""
        client.force_login(regular_user)
        
        # Создаем объекты в разных городах
        Object.objects.create(
            customer='Customer 1',
            address='г. Москва, ул. Первая, 1',
            M1=100.0
        )
        Object.objects.create(
            customer='Customer 2', 
            address='г. СПб, ул. Вторая, 2',
            M1=200.0
        )
        
        # Фильтруем по Москве
        response = client.get(reverse('to') + '?city=г. Москва')
        objects_in_context = list(response.context['objects'])
        
        assert len(objects_in_context) == 1
        assert 'Москва' in objects_in_context[0].address

    def test_object_filtering_by_colors(self, client, regular_user, test_object):
        """Тестирование фильтрации объектов по цветам"""
        client.force_login(regular_user)
        
        # Тестируем разные варианты фильтрации цветов
        response = client.get(reverse('to') + '?colors=green&colors=red')
        assert response.status_code == 200