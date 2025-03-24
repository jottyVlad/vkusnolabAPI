from rest_framework.routers import DefaultRouter

from users import views

router = DefaultRouter()

router.register("", views.UserViewSet, basename="user_viewset")
