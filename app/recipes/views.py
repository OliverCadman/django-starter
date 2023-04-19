from django.shortcuts import render
from recipes.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer
)
from core.models import Recipe

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class RecipeViewset(viewsets.ModelViewSet):
    """
    API view for Recipes
    Inherits from rest_framework's ModelViewSet,
    providing GET, POST, PUT, PATCH and DELETE routes.
    """
    serializer_class = RecipeDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Recipe.objects.all()

    def get_queryset(self):
        return self.queryset.filter(
            user=self.request.user
        ).order_by('-id')

    def get_serializer_class(self):
        """
        Returns the RecipeSerializer if 
        action is list. Otherwise, return default
        RecipeDetailSerializer
        """

        if self.action == 'list':
            return RecipeSerializer
        
        return self.serializer_class
    
    def perform_create(self, serializer):
        """Assign the user who created the recipe, to the recipe."""

        serializer.save(user=self.request.user)
