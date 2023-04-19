"""Tests for the User API"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status


def create_user(**params):
    return get_user_model().objects.create_user(**params)


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


class PublicUserAPITests(TestCase):
    """Test Public API Endpoints for User API"""

    def setUp(self):
        self.client = APIClient()
    
    def test_create_user_successful(self):
        """Test creating a new user is successful"""

        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test User'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)
    
    def test_create_user_with_existing_email_error(self):
        """Test 400 error if user created with existing email"""

        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test User'
        }

        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_invalid_password_error(self):
        """Test 400 error if user created with invalid password"""

        payload = {
            'email': 'test@example.com',
            'password': 'test',
            'name': 'TestUser'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        )
        self.assertFalse(user_exists)

    def test_create_token_success(self):
        """Test creating a token for user is successful"""

        user_details = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test User'
        }

        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password']
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)
    
    def test_create_token_bad_password(self):
        """Test 400 response if token url called with bad password"""

        user_details = {
            'email': 'test@example.com',
            'password': 'goodpassword123',
            'name': 'Test User'
        }

        create_user(**user_details)

        payload = {
            'email': 'test@example.com',
            'password': 'badpassword123'
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)
    
    def test_create_token_blank_password_error(self):
        """Test 400 response if request made with blank password"""

        payload = {
            'email': 'test@example.com',
            'password': ''
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)
