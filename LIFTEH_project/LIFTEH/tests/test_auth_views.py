import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestLoginView:
    def test_login_get(self, client):
        response = client.get(reverse('login'))
        assert response.status_code == 200
        assert 'login.html' in [t.name for t in response.templates]

    def test_login_post_success(self, client, regular_user):
        response = client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        assert response.status_code == 302
        assert response.url == reverse('to')

    def test_login_post_failure(self, client):
        response = client.post(reverse('login'), {
            'username': 'wrong',
            'password': 'wrong'
        })
        assert response.status_code == 200
        assert 'error' in response.context

@pytest.mark.django_db
class TestHomeView:
    def test_home_view(self, client):
        response = client.get(reverse('home'))
        assert response.status_code == 200
        assert 'home.html' in [t.name for t in response.templates]

@pytest.mark.django_db
class TestToView:
    def test_to_view_requires_login(self, client):
        response = client.get(reverse('to'))
        assert response.status_code == 302  # Redirect to login

    def test_to_view_authenticated(self, client, regular_user):
        client.force_login(regular_user)
        response = client.get(reverse('to'))
        assert response.status_code == 200
        assert 'to.html' in [t.name for t in response.templates]

    def test_to_view_context_data(self, client, regular_user, test_object):
        client.force_login(regular_user)
        response = client.get(reverse('to'))
        
        context = response.context
        assert 'month' in context
        assert 'objects' in context
        assert 'problems' in context
        assert 'avrs' in context