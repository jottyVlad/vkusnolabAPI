"""
API endpoints для работы с историей чатов.

Модуль содержит ViewSet для:
- Истории чатов (ChatHistory)
- Управления историей сообщений пользователя с ИИ
"""

from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import ChatHistory
from .serializers import ChatHistorySerializer


class ChatHistoryViewSet(
    mixins.ListModelMixin,       # GET /chat_history/ (список)
    mixins.CreateModelMixin,     # POST /chat_history/ (создание)
    viewsets.GenericViewSet,     # Базовый класс
    ):
    """
    ViewSet для работы с историей чатов пользователя.

    Поддерживает:
    - Создание новых записей чата
    - Просмотр своей истории чатов
    - Удаление записей
    - Фильтрацию по дате и типу отправителя

    Права доступа:
    - Только для аутентифицированных пользователей
    - Каждый пользователь видит только свою историю
    """
    queryset = ChatHistory.objects.all()
    serializer_class = ChatHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает только историю чатов текущего пользователя.
        Для анонимных пользователей возвращает пустой queryset.
        """
        user = self.request.user
        if not user.is_authenticated:
            return self.queryset.none()
        return self.queryset.filter(user_id=user)

    def perform_create(self, serializer):
        """
        Автоматически привязывает запись чата к текущему пользователю.
        Проверяет корректность типа отправителя через сериализатор.
        """
        serializer.save(user_id=self.request.user)

    @swagger_auto_schema(
        operation_description="Создание новой записи в истории чата",
        responses={
            201: "Запись успешно создана",
            400: "Неверные входные данные",
            403: "Доступ запрещен"
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Создает новую запись в истории чата.
        Автоматически назначает:
        - Текущего пользователя как владельца записи
        - Текущую дату и время
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {
                "message": "Chat message saved successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        operation_description="Получение истории чатов пользователя",
        responses={
            200: ChatHistorySerializer(many=True),
            403: "Доступ запрещен"
        }
    )
    def list(self, request, *args, **kwargs):
        """
        Возвращает отфильтрованную историю чатов текущего пользователя.
        Поддерживает пагинацию и фильтрацию через query-параметры.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def clear_history(self, request):
        """
        Очищает всю историю чатов текущего пользователя.

        Returns:
            Response: Сообщение о количестве удаленных записей
        """
        count, _ = self.get_queryset().delete()
        return Response(
            {"message": f"Deleted {count} chat history records"},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def ai_messages(self, request):
        """
        Возвращает только сообщения от ИИ (sender_type='AI')
        для текущего пользователя.
        """
        ai_messages = self.get_queryset().filter(sender_type='AI')
        serializer = self.get_serializer(ai_messages, many=True)
        return Response(serializer.data)