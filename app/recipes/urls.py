"""URL Mappings for the Recipe API"""

from django.urls import path, include
from recipes import views

from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('recipes', views.RecipeViewset)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]
