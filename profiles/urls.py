from django.urls import path
from django.views.decorators.cache import cache_page
from django.conf import settings
from rest_framework.routers import DefaultRouter

from profiles import views

urlpatterns = [
    path('me/', cache_page(settings.CACHE_MIDDLEWARE_SECONDS)(views.ProfileView.as_view()), name='profile-me'),
    path('<str:username>/', cache_page(settings.CACHE_MIDDLEWARE_SECONDS)(views.ProfileByUsernameView.as_view()), name='profile-by-username'),
]