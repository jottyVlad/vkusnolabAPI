from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Recipe, Likes
from .serializers import RecipeSerializer


class RecipeViewSet(viewsets.ModelViewSet):
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
        instance = self.get_object()

        # Проверка, что пользователь - автор рецепта
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
        """Действие для добавления/удаления лайка рецепту"""
        recipe = self.get_object()
        user = request.user

        # Проверяем, есть ли уже лайк
        like, created = Likes.objects.get_or_create(
            recipe_id=recipe,
            user_id=user
        )

        if not created:
            # Если лайк уже был - удаляем его (анлайк)
            like.delete()
            return Response({"status": "unliked"})

        return Response({"status": "liked"})