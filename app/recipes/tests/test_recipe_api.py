"""Unit Tests for various recipe API endpoints and methods"""

from decimal import Decimal

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe
from recipes.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer
)


RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """Get a url for a given recipe"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    """Helper function to create a recipe with default values"""

    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 55,
        'price': Decimal('5.55'),
        'description': 'Test Description',
        'link': 'https://example.com/sample-recipe.pdf'
    }

    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)

    return recipe


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicAPITests(TestCase):
    """Test public API requests"""

    def setUp(self):
        self.client = APIClient()
    
    def test_api_request_unauthorized(self):
        """Test 401 error for unauthorized GET request"""

        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAPITests(TestCase):
    """Test Authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='test@example.com', password='testpass123')

        self.client.force_authenticate(self.user)
    
    def test_list_recipes_successful(self):
        """Test listing recipes retrieves 200 response and data"""

        create_recipe(self.user)
        create_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.data, serializer.data)
    
    def test_recipe_list_limited_to_auth_user(self):
        """Test listing recipes is limited to only the user who created the recipe."""

        other_user = create_user(
            email='other@example.com',
            password='testpass123'
        )

        create_recipe(other_user)
        create_recipe(self.user)

        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test getting a recipe detail from the API"""

        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
    
    def test_create_recipe(self):
        """Test POST request to create a recipe"""

        payload = {
            'title': 'Sample Recipe',
            'time_minutes': 10,
            'price': Decimal('5.55'),
            'description': 'Sample Description'
        }

        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        
        self.assertEqual(recipe.user, self.user)
    
    def test_partial_update(self):
        """Test PATCH request for Recipe detail URL"""

        original_link = 'https://example.com/sample.pdf'

        recipe = create_recipe(
            user=self.user,
            title='Sample Recipe Title',
            link=original_link
        )

        payload = {
            'title': 'New Recipe Title'
        }

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.user, self.user)
        self.assertEqual(recipe.link, original_link)

    def test_full_update(self):
        """Test PUT request to Recipe Detail API"""
        recipe = create_recipe(
            user=self.user,
            title='Sample Title',
            time_minutes=10,
            link='https://example.com/sample.pdf',
            description='Sample Recipe Description'
        )

        payload = {
            'title': 'New Title',
            'time_minutes': 20,
            'link': 'https://example.com/new-sample.pdf',
            'description': 'New Recipe Description',
            'price': Decimal('5.55')
        }

        url = detail_url(recipe.id)
        res = self.client.put(url, payload)
        print(res.content)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)
    
    def test_update_user_returns_error(self):
        """Test changing recipe user results in error"""

        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=self.user)
        payload = {'user': new_user.id}

        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test making DELETE request successful"""

        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe_error(self):
        """Test deleting another user's recipe raises an error."""
        new_user = create_user(
            email='user2@example.com', password='testpass123'
        )

        recipe = create_recipe(user=new_user)
        url = detail_url(recipe.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

