"""Views for the User API"""

from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user import serializers


class CreateUserView(generics.CreateAPIView):
    """
    View to create a new user.

    Handles HTTP POST method to create new user object in DB
    """

    serializer_class = serializers.UserSerializer


class TokenAPIView(ObtainAuthToken):
    """View to generate authentication token."""

    serializer_class = serializers.TokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES