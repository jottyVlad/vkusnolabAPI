# Generated by Django 5.1.8 on 2025-05-04 11:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.FloatField()),
                ('visible_type_of_count', models.CharField(max_length=25)),
            ],
        ),
        migrations.RenameModel(
            old_name='Comments',
            new_name='Comment',
        ),
        migrations.RenameModel(
            old_name='Likes',
            new_name='Like',
        ),
        migrations.RemoveField(
            model_name='recipeingredients',
            name='id_ingredient',
        ),
        migrations.RemoveField(
            model_name='recipeingredients',
            name='id_recipe',
        ),
        migrations.RemoveConstraint(
            model_name='like',
            name='unique_likes_recipe',
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='author_id',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='recipe_id',
            new_name='recipe',
        ),
        migrations.RenameField(
            model_name='like',
            old_name='recipe_id',
            new_name='recipe',
        ),
        migrations.RenameField(
            model_name='like',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='author_id',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='searchhistory',
            old_name='user_id',
            new_name='user',
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, default=None, null=True, upload_to=''),
        ),
        migrations.AlterUniqueTogether(
            name='like',
            unique_together={('recipe', 'user')},
        ),
        migrations.RenameModel(
            old_name='Ingredients',
            new_name='Ingredient',
        ),
        migrations.AddField(
            model_name='recipeingredient',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipe.ingredient'),
        ),
        migrations.AddField(
            model_name='recipeingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipe.recipe'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(through='recipe.RecipeIngredient', to='recipe.ingredient'),
        ),
        migrations.DeleteModel(
            name='RecipeIngredients',
        ),
        migrations.AlterUniqueTogether(
            name='recipeingredient',
            unique_together={('recipe', 'ingredient')},
        ),
    ]
