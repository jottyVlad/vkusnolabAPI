from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipe.serializers import RecipeWithoutAuthorSerializer


class ProfileSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email', 'bio', 'profile_picture', 'recipes')
        read_only_fields = ('id', 'username', 'recipes')

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        return RecipeWithoutAuthorSerializer(recipes, many=True).data
