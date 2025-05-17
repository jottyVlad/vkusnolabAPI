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
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import Recipe, Like, Ingredient, RecipeIngredient, SearchHistory, Comment, Cart
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    RecipeSerializer,
    IngredientsSerializer,
    RecipeIngredientSerializer,
    LikesSerializer,
    SearchHistorySerializer,
    CommentsSerializer, CartReadSerializer, CartWriteSerializer
)


class RecipePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


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
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = RecipePagination
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    http_method_names = ['get', 'post', 'put', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    @swagger_auto_schema(
        operation_description="Создание нового рецепта",
        responses={
            201: "Рецепт успешно создан",
            400: "Неверные входные данные"
        },
        request_body=RecipeSerializer,
    )
    def create(self, request, *args, **kwargs):
        """Создает новый рецепт и автоматически назначает текущего пользователя автором"""
        data = request.data
        # data['ingredients'] = [RecipeIngredientSerializer(data=i) for i in json.loads(data.pop('ingredients')[0])]
        serializer = self.get_serializer(data=data)
        # print(request.data['ingredients'])
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)

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

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("Вы не можете удалить чужой рецепт")
        instance.delete()

    def list(self, request, *args, **kwargs):
        if request.user.is_authenticated and (text := request.query_params.get("search")):
            last_search = SearchHistory.objects.filter(user__id=request.user.id).last()
            if last_search is None or (last_search.text != text):
                search = SearchHistory(text=text, user=request.user)
                search.save()
        return super().list(request, args, kwargs)
class IngredientsViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с ингредиентами.

    Позволяет:
    - Просматривать список всех ингредиентов
    - Создавать новые ингредиенты
    - Обновлять и удалять существующие
    """
    queryset = Ingredient.objects.all()
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
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer
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
    queryset = Like.objects.all()
    serializer_class = LikesSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Liked successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


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
        """
        if self.request.user.is_authenticated:
            return (self.queryset
                    .filter(user=self.request.user.id)
                    .order_by('-created_at'))[:5]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(
            {
                "message": "Liked successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class CommentsViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с комментариями к рецептам.

    Позволяет:
    - Просматривать комментарии
    - Оставлять новые комментарии
    - Удалять/редактировать свои комментарии
    """
    serializer_class = CommentsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Comment.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['recipe__id']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("Вы не можете удалить чужой комментарий")
        instance.delete()


class CartViewSet(viewsets.ModelViewSet):
    """
    GET (list/retrieve) — возвращает все записи корзины текущего пользователя
      без тела запроса.
    POST/PUT/PATCH — CRUD по полю text_recipe_ingredient.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['text_recipe_ingredient']

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return CartReadSerializer
        return CartWriteSerializer

    def create(self, request, *args, **kwargs):
        """
        Принимает как одиночный объект, так и список объектов
        ПРИМЕР!
        [
          {"text_recipe_ingredient": "400гр Мука"},
          {"text_recipe_ingredient": "2шт Яйцо"}
        ]
        """
        data = request.data
        many = isinstance(data, list)
        write_ser = CartWriteSerializer(
            data=data,
            many=many,
            context={'request': request}
        )
        write_ser.is_valid(raise_exception=True)
        items = write_ser.save()

        # items — либо один объект, либо список
        read_ser = CartReadSerializer(
            items,
            many=many,
            context={'request': request}
        )
        return Response({'data': read_ser.data}, status=status.HTTP_201_CREATED)


    @swagger_auto_schema(
        request_body=None,
        responses={
            200: CartReadSerializer(many=True)
        })
    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        ser = CartReadSerializer(qs, many=True, context={'request': request})
        return Response({'data': ser.data})


    @swagger_auto_schema(
        request_body=CartWriteSerializer,
        responses={
            200: CartReadSerializer
        })
    def update(self, request, *args, **kwargs):
        inst = self.get_object()
        write_ser = self.get_serializer(inst, data=request.data, context={'request': request})
        write_ser.is_valid(raise_exception=True)
        item = write_ser.save()
        read_ser = CartReadSerializer(item, context={'request': request})
        return Response({'data': read_ser.data}, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        request_body=CartWriteSerializer,
        responses={
            200: CartReadSerializer
        })
    def partial_update(self, request, *args, **kwargs):
        inst = self.get_object()
        write_ser = self.get_serializer(inst, data=request.data, partial=True,
                                        context={'request': request})
        write_ser.is_valid(raise_exception=True)
        item = write_ser.save()
        read_ser = CartReadSerializer(item, context={'request': request})
        return Response({'data': read_ser.data}, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        request_body=None,
        responses={
            204: 'No Content'
        })
    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)