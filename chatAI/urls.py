from rest_framework.routers import DefaultRouter

from recipe import views

router = DefaultRouter()

router.register('chat_history', views.ChatHistoryViewSet, basename='rchat_history_viewset')
