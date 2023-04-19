"""Serializers for the recipe API view"""

from rest_framework.serializers import ModelSerializer
from core.models import Recipe


class RecipeSerializer(ModelSerializer):
    """Serializer for individual recipe model"""

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for the Recipe Detail API"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']