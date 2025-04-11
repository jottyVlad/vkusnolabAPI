"""Определяет в каком виде приходят и возвращаются данные от клиентов"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from recipe.models import Recipe, Ingredients, RecipeIngredients, Likes, SearchHistory, Comments


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Recipe.

    Обрабатывает создание и обновление рецептов. Включает валидацию:
    - Время готовки должно быть > 0
    - Количество порций должно быть > 0
    - Автор обязателен
    """
    author = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        source='author_id',
        help_text="ID пользователя-автора рецепта"
    )

    class Meta:
        model = Recipe
        fields = '__all__'
        extra_kwargs = {
            'author_id': {'read_only': True},
            'title': {
                'required': True,
                'max_length': 100,
                'help_text': "Название рецепта (макс. 100 символов)"
            },
            'description': {
                'max_length': 2000,
                'help_text': "Краткое описание рецепта (макс. 2000 символов)"
            },
            'instructions': {
                'max_length': 100000,
                'help_text': "Пошаговые инструкции приготовления"
            },
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
            'is_active': {
                'default': True,
                'help_text': "Флаг активности рецепта"
            },
            'is_private': {
                'default': False,
                'help_text': "Приватный рецепт виден только автору"
            },
            'servings': {
                'min_value': 1,
            },
            'cooking_time_minutes': {
                'min_value': 1,
            }
        }

    def validate(self, data):
        """Проверка валидности данных рецепта."""
        if data.get('cooking_time_minutes', 0) <= 0:
            raise serializers.ValidationError({
                "cooking_time_minutes": "Время готовки должно быть больше 0!"
            })
        if data.get('servings', 0) <= 0:
            raise serializers.ValidationError({
                "servings": "Количество порций должно быть больше 0!"
            })
        return data


class IngredientsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ingredients.

    Обрабатывает основные операции с ингредиентами.
    """

    class Meta:
        model = Ingredients
        fields = '__all__'
        extra_kwargs = {
            'name': {
                'required': True,
                'max_length': 100,
                'help_text': "Название ингредиента (макс. 100 символов)"
            }
        }


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для связи рецептов и ингредиентов (RecipeIngredients).

    Позволяет:
    - Указывать количество ингредиента в граммах
    - Задавать формат отображения количества
    """
    id_ingredient = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Ingredients.objects.all(),
        help_text="Название ингредиента"
    )
    id_recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        help_text="ID связанного рецепта"
    )

    class Meta:
        model = RecipeIngredients
        fields = '__all__'
        extra_kwargs = {
            'id_ingredient': {'required': True},
            'id_recipe': {'required': True},
            'count_in_grams': {
                'min_value': 1,
                'help_text': "Количество в граммах (минимум 1)"
            },
            'visible_type_of_count': {
                'max_length': 25,
                'help_text': "Формат отображения количества"
            }
        }


class LikesSerializer(serializers.ModelSerializer):
    """
    Сериализатор для лайков (Likes).

    Автоматически устанавливает:
    - Пользователя из запроса
    - Текущую дату создания
    """

    class Meta:
        model = Likes
        fields = '__all__'
        extra_kwargs = {
            'user_id': {
                'read_only': True,
                'help_text': "Автоматически устанавливается из запроса"
            },
            'recipe_id': {
                'help_text': "ID рецепта, который лайкнули"
            },
            'created_at': {
                'read_only': True,
                'help_text': "Дата создания лайка"
            },
        }


class CommentsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для комментариев (Comments).

    Особенности:
    - Автор устанавливается автоматически
    - Дата создания не редактируется
    - Текст комментария обязателен
    """

    class Meta:
        model = Comments
        fields = '__all__'
        extra_kwargs = {
            'author_id': {
                'read_only': True,
                'help_text': "Автоматически устанавливается из запроса"
            },
            'recipe_id': {
                'required': True,
                'help_text': "ID рецепта, к которому относится комментарий"
            },
            'created_at': {
                'read_only': True,
                'help_text': "Дата создания комментария"
            },
            'comment_text': {
                'required': True,
                'max_length': 2000,
                'help_text': "Текст комментария (макс. 2000 символов)"
            },
        }


class SearchHistorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для истории поиска (SearchHistory).

    Автоматически сохраняет:
    - Пользователя из запроса
    - Текущую дату и время поиска
    """

    class Meta:
        model = SearchHistory
        fields = '__all__'
        extra_kwargs = {
            'user_id': {
                'read_only': True,
                'help_text': "Автоматически устанавливается из запроса"
            },
            'created_at': {
                'read_only': True,
                'help_text': "Дата и время поискового запроса"
            },
            'text': {
                'required': True,
                'max_length': 100,
                'help_text': "Текст поискового запроса (макс. 100 символов)"
            },
        }