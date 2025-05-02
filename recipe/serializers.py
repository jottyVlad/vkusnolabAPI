"""Определяет в каком виде приходят и возвращаются данные от клиентов"""
import json

from rest_framework import serializers

import users
from recipe.models import Recipe, Ingredient, RecipeIngredient, Like, SearchHistory, Comment
from users.serializers import UserProfileSerializer


class RecipeIngredientSerializer(serializers.ModelSerializer):
    # Принимаем ingredient как ID (PrimaryKeyRelatedField)
    ingredient = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        write_only=True  # Поле только для записи
    )
    count = serializers.FloatField()
    visible_type_of_count = serializers.CharField()

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'count', 'visible_type_of_count']


class RecipeSerializer(serializers.ModelSerializer):
    # ingredients = RecipeIngredientSerializer(many=True, required=True)
    ingredients = serializers.JSONField(required=True)
    author = users.serializers.UserProfileSerializer(read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author', 'created_at', 'updated_at')

    # def validate_ingredients(self, value):
    #     try:
    #         # Пробуем распарсить JSON-строку
    #         print(value)
    #         ingredients = json.loads(value[0])
    #         if not isinstance(ingredients, list):
    #             raise serializers.ValidationError("Ingredients must be a list")
    #         return ingredients
    #     except json.JSONDecodeError:
    #         raise serializers.ValidationError("Invalid JSON format for ingredients")

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['ingredient'])
            # ingredient = RecipeIngredientSerializer(data=ingredient_data)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                count=ingredient_data['count'],
                visible_type_of_count=ingredient_data['visible_type_of_count']
            )

        return recipe

    def to_representation(self, instance: Recipe):
        """Кастомное представление для вывода"""
        data = dict()
        data['id'] = instance.id
        data['author'] = UserProfileSerializer(instance.author).data
        data['ingredients'] = [
            {
                'ingredient': ri.ingredient.id,
                'name': ri.ingredient.name,
                'count': ri.count,
                'visible_type_of_count': ri.visible_type_of_count
            }
            for ri in instance.recipeingredient_set.all()
        ]
        data['title'] = instance.title
        data['description'] = instance.description
        data['image'] = instance.image.url if instance.image else None
        data['instructions'] = instance.instructions
        data['servings'] = instance.servings
        data['created_at'] = instance.created_at
        data['updated_at'] = instance.updated_at
        data['is_active'] = instance.is_active
        data['is_private'] = instance.is_private
        return data


class IngredientsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ingredients.

    Обрабатывает основные операции с ингредиентами.
    """

    class Meta:
        model = Ingredient
        fields = '__all__'
        extra_kwargs = {
            'name': {
                'required': True,
                'max_length': 100,
                'help_text': "Название ингредиента (макс. 100 символов)"
            }
        }


class LikesSerializer(serializers.ModelSerializer):
    """
    Сериализатор для лайков (Likes).

    Автоматически устанавливает:
    - Пользователя из запроса
    - Текущую дату создания
    """

    user = users.serializers.UserProfileSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ('recipe', 'created_at', 'user',)
        read_only_fields = ('created_at',)
        extra_kwargs = {
            'recipe': {
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
    author = users.serializers.UserProfileSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('recipe', 'created_at', 'comment_text', 'author',)
        read_only_fields = ('created_at',)
        extra_kwargs = {
            'recipe': {
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

    user = users.serializers.UserProfileSerializer(read_only=True)

    class Meta:
        model = SearchHistory
        fields = ('created_at', 'text', 'user',)
        read_only_fields = ('created_at',)
        extra_kwargs = {
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