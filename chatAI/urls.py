from chatAI import views
from chatAI.utils import CacheRouter

router = CacheRouter()

router.register('chat_history', views.ChatHistoryViewSet, basename='chat_history_viewset')
