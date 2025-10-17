import pytest
import json
from django.urls import reverse
from LIFTEH.models import Problem
from django.contrib.auth import get_user_model

User = get_user_model()

class TestProblems:
    def test_add_problem_get(self, client, regular_user):
        """Тест получения формы добавления проблемы"""
        client.force_login(regular_user)
        response = client.get(reverse('add_problem'))
        assert response.status_code == 302  # Redirect for GET

    def test_add_problem_post(self, client, regular_user):
        """Тест добавления новой проблемы"""
        client.force_login(regular_user)
        
        response = client.post(reverse('add_problem'), {
            'name': 'Test problem name'
        })
        
        assert response.status_code == 302  # Redirect after success
        assert Problem.objects.filter(name='Test problem name').exists()

    def test_add_problem_ajax(self, client, regular_user):
        """Тест добавления проблемы через AJAX"""
        client.force_login(regular_user)
        
        response = client.post(
            reverse('add_problem'),
            {'name': 'AJAX test problem'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert Problem.objects.filter(name='AJAX test problem').exists()

    def test_update_problem_status(self, client, regular_user, test_problem):
        """Тест обновления статуса проблемы"""
        client.force_login(regular_user)
        
        response = client.post(
            reverse('update_problem_status', args=[test_problem.id]),
            data=json.dumps({'is_completed': True}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert data['is_completed'] == True
        
        # Проверяем, что статус обновился в базе
        test_problem.refresh_from_db()
        assert test_problem.is_completed == True

    def test_edit_problem(self, client, regular_user, test_problem):
        """Тест редактирования проблемы"""
        client.force_login(regular_user)
        
        response = client.post(
            reverse('edit_problem', args=[test_problem.id]),
            {
                'name': 'Updated problem name',
                'created_date': '2024-01-15'
            }
        )
        
        assert response.status_code == 302  # Redirect after success
        
        test_problem.refresh_from_db()
        assert test_problem.name == 'Updated problem name'

    def test_delete_problem(self, client, regular_user, test_problem):
        """Тест удаления проблемы"""
        client.force_login(regular_user)
        
        problem_id = test_problem.id
        response = client.post(reverse('delete_problem', args=[problem_id]))
        
        assert response.status_code == 302  # Redirect after success
        assert not Problem.objects.filter(id=problem_id).exists()

    def test_problem_access_control(self, client, regular_user, admin_user, test_problem):
        """Тест контроля доступа к проблемам"""
        # Обычный пользователь не может редактировать чужие проблемы
        another_user = User.objects.create_user(
            username='another', 
            password='testpass123'
        )
        client.force_login(another_user)
        
        response = client.post(reverse('edit_problem', args=[test_problem.id]))
        # Должен быть редирект или ошибка доступа
        assert response.status_code in [302, 403]

        # Суперпользователь может редактировать любые проблемы
        client.force_login(admin_user)
        response = client.post(
            reverse('edit_problem', args=[test_problem.id]),
            {'name': 'Admin updated', 'created_date': '2024-01-15'}
        )
        assert response.status_code == 302