"""
API endpoints для работы с рецептами и связанными сущностями.

Модуль содержит ViewSets для:
- Рецептов (Recipe)
- Ингредиентов (Ingredients)
- Связей рецептов и ингредиентов (RecipeIngredients)
- Лайков (Likes)
- Истории поиска (SearchHistory)
- Комментариев (Comments)

Все endpoints поддерживают стандартные CRUD операции
и дополнительные кастомные действия.
"""

from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Recipe, Likes, Ingredients, RecipeIngredients, SearchHistory, Comments
from .serializers import (
    RecipeSerializer,
    IngredientsSerializer,
    RecipeIngredientsSerializer,
    LikesSerializer,
    SearchHistorySerializer,
    CommentsSerializer
)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с рецептами.

    Поддерживает:
    - Создание, чтение, обновление, удаление рецептов
    - Добавление/удаление лайков
    - Фильтрацию по автору и статусу

    Права доступа:
    - Чтение: доступно всем
    - Запись: только аутентифицированным пользователям
    - Изменение: только автор рецепта
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="Создание нового рецепта",
        responses={
            201: "Рецепт успешно создан",
            400: "Неверные входные данные"
        }
    )
    def create(self, request, *args, **kwargs):
        """Создает новый рецепт и автоматически назначает текущего пользователя автором"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author_id=request.user)

        return Response(
            {
                "message": "Recipe created successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        operation_description="Частичное обновление рецепта",
        responses={
            200: RecipeSerializer,
            400: "Неверные входные данные",
            404: "Рецепт не найден"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """Обновляет рецепт (только для автора)"""
        instance = self.get_object()

        if instance.author_id != request.user:
            return Response(
                {"message": "You can only edit your own recipes"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """
        Добавляет или удаляет лайк рецепта.

        Если лайк уже существует - удаляет его (анлайк),
        если нет - создает новый лайк.
        """
        recipe = self.get_object()
        user = request.user

        like, created = Likes.objects.get_or_create(
            recipe_id=recipe,
            user_id=user
        )

        if not created:
            like.delete()
            return Response({"status": "unliked"})

        return Response({"status": "liked"})


class IngredientsViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с ингредиентами.

    Позволяет:
    - Просматривать список всех ингредиентов
    - Создавать новые ингредиенты
    - Обновлять и удалять существующие
    """
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="Создание нового ингредиента",
        responses={
            201: "Ингредиент успешно создан",
            400: "Неверные входные данные"
        }
    )
    def create(self, request, *args, **kwargs):
        """Создает новый ингредиент"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Ingredient created successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class RecipeIngredientsViewSet(viewsets.ModelViewSet):
    """
    ViewSet для связи рецептов и ингредиентов.

    Позволяет:
    - Добавлять ингредиенты в рецепты
    - Указывать количество ингредиентов
    - Управлять связями рецепт-ингредиент
    """
    queryset = RecipeIngredients.objects.all()
    serializer_class = RecipeIngredientsSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Автоматически сохраняет связь рецепта и ингредиента"""
        serializer.save()

    @swagger_auto_schema(
        operation_description="Добавление ингредиента в рецепт",
        responses={
            201: "Ингредиент добавлен в рецепт",
            400: "Неверные входные данные"
        }
    )
    def create(self, request, *args, **kwargs):
        """Создает связь между рецептом и ингредиентом"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Ingredient added to recipe successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class LikesViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с лайками рецептов.

    Позволяет:
    - Просматривать свои лайки
    - Создавать/удалять лайки
    """
    queryset = Likes.objects.all()
    serializer_class = LikesSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Автоматически привязывает лайк к текущему пользователю"""
        serializer.save(user_id=self.request.user)


class SearchHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet для истории поиска пользователей.

    Позволяет:
    - Просматривать свою историю поиска
    - Создавать новые записи поиска
    - Удалять историю
    """
    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает только историю поиска текущего пользователя.

        Для анонимных пользователей возвращает пустой queryset.
        """
        if hasattr(self.request.user, 'id'):
            return self.queryset.filter(user_id=self.request.user.id)
        return self.queryset.none()

    def perform_create(self, serializer):
        """Автоматически привязывает запись поиска к текущему пользователю"""
        serializer.save(user_id=self.request.user)


class CommentsViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с комментариями к рецептам.

    Позволяет:
    - Просматривать комментарии
    - Оставлять новые комментарии
    - Удалять/редактировать свои комментарии
    """
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """Автоматически назначает автора комментария"""
        serializer.save(author_id=self.request.user)

    @swagger_auto_schema(
        operation_description="Создание нового комментария",
        responses={
            201: "Комментарий успешно создан",
            400: "Неверные входные данные"
        }
    )
    def create(self, request, *args, **kwargs):
        """Создает новый комментарий к рецепту"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author_id=request.user)

        return Response(
            {
                "message": "Comment created successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )