from rest_framework.routers import DefaultRouter

from recipe import views

router = DefaultRouter()

router.register('', views.RecipeViewSet, basename='recipe_viewset')