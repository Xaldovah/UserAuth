import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from backend.models import User, Organisation
import jwt
from django.conf import settings
from datetime import datetime, timedelta

@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
def test_register_user_success(client):
    url = reverse('register')
    data = {
            "first_name": "Morry",
            "last_name": "Doe",
            "email": "morry.doe@example.com",
            "password": "password123",
            "phone": "123456789"
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['data']['user']['first_name'] == "Morry"
    assert response.data['data']['user']['email'] == "morry.doe@example.com"
    assert "accessToken" in response.data['data']
    user = User.objects.get(email="morry.doe@example.com")
    org = Organisation.objects.filter(users=user).first()
    assert org is not None
    assert org.name == "Morry's Organisation"


@pytest.mark.django_db
def test_register_user_missing_fields(client):
    url = reverse('register')
    data = {
            "first_name": "Morry",
            "email": "morry.doe@example.com",
            "password": "password123"
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert any(error['field'] == 'last_name' for error in response.data['errors'])


@pytest.mark.django_db
def test_register_user_duplicate_email(client):
    User.objects.create_user(email="morry.doe@example.com", first_name="Morry", last_name="Doe", password="password123")
    url = reverse('register')
    data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "morry.doe@example.com",
            "password": "password123",
            "phone": "123456789"
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert any(error['field'] == 'email' for error in response.data['errors'])


@pytest.mark.django_db
def test_login_user_success(client):
    user = User(email="morry.doe@example.com", first_name="Morry", last_name="Doe")
    user.set_password("password123")
    user.save()
    url = reverse('login')
    data = {
            "email": "morry.doe@example.com",
            "password": "password123"
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert 'accessToken' in response.data['data']


@pytest.mark.django_db
def test_login_user_fail(client):
    url = reverse('login')
    data = {
            "email": "morry.doe@example.com",
            "password": "wrongpassword"
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['message'] == "Authentication failed"


@pytest.mark.django_db
def test_token_generation(client):
    user = User(email="morry.doe@example.com", first_name="Morry", last_name="Doe")
    user.set_password("password123")
    user.save()
    token = jwt.encode({
        'user_id': str(user.user_id),
        'exp': datetime.utcnow() + timedelta(seconds=5)
    }, settings.SECRET_KEY, algorithm='HS256')
    decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    assert decoded_token['user_id'] == str(user.user_id)


@pytest.mark.django_db
def test_access_protected_endpoint_without_token(client):
    url = reverse('organisations')
    response = client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_access_protected_endpoint_with_invalid_token(client):
    url = reverse('organisations')
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + 'invalidtoken')
    response = client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_cannot_access_other_user_organisations(client):
    user1 = User.objects.create_user(email="morry.doe@example.com", first_name="Morry", last_name="Doe", password="password123")
    user2 = User.objects.create_user(email="jane.doe@example.com", first_name="Jane", last_name="Doe", password="password123")
    org = Organisation.objects.create(name="Morry's Organisation")
    org.users.add(user1)
    token = jwt.encode({'user_id': str(user2.user_id)}, settings.SECRET_KEY, algorithm='HS256')
    url = reverse('organisation-detail', kwargs={'org_id': org.org_id})
    client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
    response = client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
