from rest_framework.routers import DefaultRouter

from users import views
# from users.utils import CacheRouter

# router = CacheRouter()
router = DefaultRouter()

router.register('', views.UserRegistrationViewSet, basename='user_reg_viewset')
router.register('', views.UserViewSet, basename='user_viewset')
