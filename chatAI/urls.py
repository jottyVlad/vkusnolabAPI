from rest_framework.routers import DefaultRouter

from chatAI import views

router = DefaultRouter()

router.register('chat_history', views.ChatHistoryViewSet, basename='chat_history_viewset')
