from users import views
from users.utils import CacheRouter

router = CacheRouter()

router.register('', views.UserRegistrationViewSet, basename='user_reg_viewset')
router.register('', views.UserViewSet, basename='user_viewset')
