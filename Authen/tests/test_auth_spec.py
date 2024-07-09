from django.test import TestCase
from rest_framework.test import APIClient
from backend.models import User, Organisation

class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        response = self.client.post('/auth/register', {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'password123',
            'phone': '1234567890'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('accessToken', response.data['data'])

    def test_login_user(self):
        user = User.objects.create_user(userId='123', email='john@example.com', firstName='John', lastName='Doe', password='password123')
        response = self.client.post('/auth/login', {
            'email': 'john@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('accessToken', response.data['data'])

    def test_create_organisation(self):
        user = User.objects.create_user(userId='123', email='john@example.com', firstName='John', lastName='Doe', password='password123')
        self.client.force_authenticate(user=user)
        response = self.client.post('/api/organisations', {
            'name': 'New Org',
            'description': 'Description of new org'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('orgId', response.data['data'])
