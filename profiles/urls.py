from django.urls import path

from profiles import views

# urlpatterns = [
#     path('me/', cache_page(settings.CACHE_MIDDLEWARE_SECONDS)(views.ProfileView.as_view()), name='profile-me'),
#     path('<str:username>/', cache_page(settings.CACHE_MIDDLEWARE_SECONDS)(views.ProfileByUsernameView.as_view()), name='profile-by-username'),
# ]

urlpatterns = [
    path('me/', views.ProfileView.as_view(), name='profile-me'),
    path('<str:username>/', views.ProfileByUsernameView.as_view(), name='profile-by-username'),
]