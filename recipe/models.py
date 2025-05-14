from django.contrib.auth import get_user_model
from django.db import models

from baseAPI import settings

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=100)


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
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
    ingredients = models.ManyToManyField(to='Ingredient',
                                         through="RecipeIngredient")


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    count = models.FloatField()
    visible_type_of_count = models.CharField(max_length=25)

    class Meta:
        unique_together = ("recipe", "ingredient")


class Like(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('recipe', 'user')


class SearchHistory(models.Model):
    text = models.TextField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    comment_text = models.TextField(max_length=2000)


from django.conf import settings
from django.db import models

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text_recipe_ingredient = models.TextField()