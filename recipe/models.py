from django.contrib.auth import get_user_model
from django.db import models

from baseAPI import settings

User = get_user_model()

class Recipe(models.Model):
    author_id = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=2000)
    instructions = models.TextField(max_length=100000)
    cooking_time_minutes = models.IntegerField()
    servings = models.IntegerField()
    image = models.ImageField(default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_private = models.BooleanField(default=False)


class Ingredients(models.Model):
    name = models.CharField(max_length=100)


class RecipeIngredients(models.Model):
    id_ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    id_recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    count_in_grams = models.IntegerField()
    visible_type_of_count = models.CharField(max_length=25)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['id_ingredient', 'id_recipe'], name='unique_ingredient_recipe'
            )
        ]


class Likes(models.Model):
    recipe_id = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe_id', 'user_id'], name='unique_likes_recipe'
            )
        ]


class SearchHistory(models.Model):
    text = models.TextField(max_length=100)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Comments(models.Model):
    recipe_id = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    author_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    comment_text = models.TextField(max_length=2000)
