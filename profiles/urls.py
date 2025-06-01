from django.urls import path
from rest_framework.routers import DefaultRouter

from profiles import views

urlpatterns = [
    path('me/', views.ProfileView.as_view(), name='profile-me'),
    path('get/<str:username>/', views.ProfileByUsernameView.as_view(), name='profile-by-username'),
]