from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from recipe.models import Recipe, Ingredient, RecipeIngredient, Like, Comment, SearchHistory
from django.core.cache import cache

User = get_user_model()

INGREDIENTS_LIST_URL = reverse('ingredient_viewset-list')

def ingredient_detail_url(ingredient_id):
    return reverse('ingredient_viewset-detail', args=[ingredient_id])

RECIPES_LIST_URL = reverse('recipe_viewset-list')

def recipe_detail_url(recipe_id):
    return reverse('recipe_viewset-detail', args=[recipe_id])

LIKES_LIST_URL = reverse('likes_viewset-list')

def like_detail_url(like_id):
    return reverse('likes_viewset-detail', args=[like_id])

SEARCH_HISTORY_LIST_URL = reverse('search_viewset-list')

COMMENTS_LIST_URL = reverse('comments_viewset-list')

def comment_detail_url(comment_id):
    return reverse('comments_viewset-detail', args=[comment_id])


class IngredientAPITests(APITestCase):

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.ingredient = Ingredient.objects.create(name='Помидор')

    def test_list_ingredients(self):
        """Тест получения списка ингредиентов"""
        Ingredient.objects.create(name='Огурец')
        response = self.client.get(INGREDIENTS_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        self.assertTrue(any(ing['name'] == 'Помидор' for ing in response.data))
        self.assertTrue(any(ing['name'] == 'Огурец' for ing in response.data))


    def test_create_ingredient_success(self):
        """Тест успешного создания ингредиента"""
        payload = {'name': 'Картофель'}
        response = self.client.post(INGREDIENTS_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Ingredient.objects.filter(name='Картофель').exists())
        self.assertEqual(response.data['data']['name'], 'Картофель')

    def test_create_ingredient_missing_name(self):
        """Тест создания ингредиента без обязательного поля 'name'"""
        payload = {}
        response = self.client.post(INGREDIENTS_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredient_detail(self):
        """Тест получения деталей ингредиента"""
        url = ingredient_detail_url(self.ingredient.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.ingredient.name)

    def test_update_ingredient(self):
        """Тест обновления ингредиента (PATCH)"""
        url = ingredient_detail_url(self.ingredient.id)
        payload = {'name': 'Спелый помидор'}
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ingredient.refresh_from_db()
        self.assertEqual(self.ingredient.name, 'Спелый помидор')

    def test_delete_ingredient(self):
        """Тест удаления ингредиента"""
        url = ingredient_detail_url(self.ingredient.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=self.ingredient.id).exists())

    def test_unauthenticated_user_cannot_create(self):
        """Тест: неаутентифицированный пользователь не может создавать ингредиенты"""
        self.client.force_authenticate(user=None)
        payload = {'name': 'Лук'}
        response = self.client.post(INGREDIENTS_LIST_URL, payload)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class RecipeAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='recipeauthor', password='password123')
        self.other_user = User.objects.create_user(username='otheruser', password='password456')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.ingredient1 = Ingredient.objects.create(name='Мука')
        self.ingredient2 = Ingredient.objects.create(name='Яйцо')
        self.ingredient3 = Ingredient.objects.create(name='Молоко')

        self.recipe = Recipe.objects.create(
            author=self.user,
            title='Простой омлет',
            description='Классический омлет на завтрак',
            instructions='Смешать яйца и молоко, вылить на сковороду...',
            cooking_time_minutes=10,
            servings=2
        )
        RecipeIngredient.objects.create(recipe=self.recipe, ingredient=self.ingredient2, count=2, visible_type_of_count='шт')
        RecipeIngredient.objects.create(recipe=self.recipe, ingredient=self.ingredient3, count=50, visible_type_of_count='мл')

    def test_list_recipes(self):
        """Тест получения списка рецептов"""
        Recipe.objects.create(
            author=self.other_user,
            title='Блины',
            description='Тонкие блинчики',
            instructions='Смешать все...',
            cooking_time_minutes=30,
            servings=4
        )

        response = self.client.get(RECIPES_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        print(response.data)
        recipes_data = response.data['results']

        self.assertEqual(len(recipes_data), 2)

        self.assertTrue(any(r['title'] == 'Простой омлет' for r in recipes_data))
        self.assertTrue(any(r['title'] == 'Блины' for r in recipes_data))

    def test_create_recipe_success(self):
        """Тест успешного создания рецепта с ингредиентами"""
        ingredients_payload_obj = [
            {'ingredient': self.ingredient1.id, 'count': 200, 'visible_type_of_count': 'г'},
            {'ingredient': self.ingredient2.id, 'count': 3, 'visible_type_of_count': 'шт'},
        ]
        payload = {
            'title': 'Новый Пирог',
            'description': 'Очень вкусный',
            'instructions': 'Замесить тесто...',
            'cooking_time_minutes': 60,
            'servings': 8,
            'ingredients': ingredients_payload_obj,
            'is_private': False,
        }

        response = self.client.post(RECIPES_LIST_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Recipe.objects.filter(title='Новый Пирог').exists())
        new_recipe = Recipe.objects.get(title='Новый Пирог')
        self.assertEqual(new_recipe.author, self.user)
        self.assertEqual(new_recipe.recipeingredient_set.count(), 2)

        response_data = response.data['data']
        self.assertIn('ingredients', response_data)
        self.assertEqual(len(response_data['ingredients']), 2)
        self.assertTrue(any(i['name'] == 'Мука' for i in response_data['ingredients']))
        self.assertTrue(any(i['name'] == 'Яйцо' for i in response_data['ingredients']))

    def test_create_recipe_invalid_ingredients_format(self):
        """Тест создания рецепта с невалидным форматом ингредиентов (не список)"""
        payload = {
            'title': 'Неудачный Рецепт',
            'description': '...',
            'instructions': '...',
            'cooking_time_minutes': 5,
            'servings': 1,
            'ingredients': "invalid_string_format",
        }
        response = self.client.post(RECIPES_LIST_URL, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('ingredients', response.data)

    def test_create_recipe_missing_title(self):
        """Тест создания рецепта без обязательного поля 'title'"""
        ingredients_payload = [
            {'ingredient': self.ingredient1.id, 'count': 100, 'visible_type_of_count': 'г'}
        ]
        payload = {
            # 'title': 'Нет заголовка',
            'description': 'Описание есть',
            'instructions': 'Инструкция есть',
            'cooking_time_minutes': 20,
            'servings': 2,
            'ingredients': ingredients_payload,
        }
        response = self.client.post(RECIPES_LIST_URL, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_retrieve_recipe_detail(self):
        """Тест получения деталей рецепта"""
        url = recipe_detail_url(self.recipe.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.recipe.title)
        self.assertEqual(response.data['author']['username'], self.user.username)
        self.assertEqual(len(response.data['ingredients']), 2)
        self.assertTrue(any(i['name'] == 'Яйцо' for i in response.data['ingredients']))
        self.assertTrue(any(i['name'] == 'Молоко' for i in response.data['ingredients']))

    def test_delete_recipe_by_author(self):
        """Тест удаления рецепта его автором"""
        url = recipe_detail_url(self.recipe.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=self.recipe.id).exists())

    def test_delete_recipe_by_other_user_forbidden(self):
        """Тест: другой пользователь не может удалить рецепт"""
        self.client.force_authenticate(user=self.other_user)
        url = recipe_detail_url(self.recipe.id)
        response = self.client.delete(url)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_unauthenticated_user_cannot_create_recipe(self):
        """Тест: неаутентифицированный пользователь не может создать рецепт"""
        self.client.force_authenticate(user=None)
        ingredients_payload = [
            {'ingredient': self.ingredient1.id, 'count': 1, 'visible_type_of_count': 'шт'}
        ]
        payload = {
            'title': 'Анонимный рецепт',
            'description': '...',
            'instructions': '...',
            'cooking_time_minutes': 5,
            'servings': 1,
            'ingredients': ingredients_payload,
        }
        response = self.client.post(RECIPES_LIST_URL, payload, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class LikeAPITests(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

        self.author = User.objects.create_user(username='author', password='password')
        self.recipe = Recipe.objects.create(
            author=self.author, title='Рецепт для лайков', description='...',
            instructions='...', cooking_time_minutes=1, servings=1
        )

    def test_create_like_success(self):
        """Тест успешного создания лайка"""
        payload = {'recipe': self.recipe.id}
        response = self.client.post(LIKES_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Like.objects.filter(user=self.user1, recipe=self.recipe).exists())

        self.assertEqual(response.data['data']['user'], self.user1.id)
        self.assertEqual(response.data['data']['recipe'], self.recipe.id)

    def test_create_like_duplicate_fails(self):
        """Тест: нельзя лайкнуть один рецепт дважды"""
        Like.objects.create(user=self.user1, recipe=self.recipe)
        payload = {'recipe': self.recipe.id}
        response = self.client.post(LIKES_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_like_success(self):
        """Тест удаления лайка"""
        like = Like.objects.create(user=self.user1, recipe=self.recipe)
        url = like_detail_url(like.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Like.objects.filter(id=like.id).exists())

    def test_unauthenticated_user_cannot_like(self):
        """Тест: неаутентифицированный пользователь не может лайкать"""
        self.client.force_authenticate(user=None)
        payload = {'recipe': self.recipe.id}
        response = self.client.post(LIKES_LIST_URL, payload)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


class CommentCreateTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='commenter1', password='password1')
        self.user2 = User.objects.create_user(username='commenter2', password='password2')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

        self.author = User.objects.create_user(username='recipe_author', password='password')
        self.recipe = Recipe.objects.create(
            author=self.author, title='Рецепт для комментов', description='...',
            instructions='...', cooking_time_minutes=1, servings=1
        )

        self.comment = Comment.objects.create(
            author=self.user2,
            recipe=self.recipe,
            comment_text='Первый коммент от user2'
        )

    def test_create_comment_success(self):
        """Тест успешного создания комментария"""
        payload = {
            'recipe': self.recipe.id,
            'comment_text': 'Отличный рецепт!'
        }
        response = self.client.post(COMMENTS_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Comment.objects.filter(author=self.user1, recipe=self.recipe).exists())
        self.assertEqual(response.data['comment_text'], 'Отличный рецепт!')
        self.assertEqual(response.data['author']['username'], self.user1.username)
        self.assertEqual(response.data['recipe'], self.recipe.id)

    def test_create_comment_missing_text(self):
        """Тест создания комментария без текста"""
        payload = {'recipe': self.recipe.id}
        response = self.client.post(COMMENTS_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('comment_text', response.data)

    def test_list_comments_for_recipe(self):
        """Тест получения списка комментариев (можно фильтровать по recipe_id)"""

        Comment.objects.create(
            author=self.user1,
            recipe=self.recipe,
            comment_text='Второй коммент'
        )

        response_all = self.client.get(COMMENTS_LIST_URL)
        self.assertEqual(response_all.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_all.data), 2)

        response_filtered = self.client.get(COMMENTS_LIST_URL, {'recipe': self.recipe.id})
        self.assertEqual(response_filtered.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_filtered.data), 2)
        self.assertTrue(any(c['comment_text'] == 'Первый коммент от user2' for c in response_filtered.data))
        self.assertTrue(any(c['comment_text'] == 'Второй коммент' for c in response_filtered.data))

    def test_delete_comment_by_author(self):
        """Тест удаления комментария его автором"""

        comment_to_delete = Comment.objects.create(
            author=self.user1,
            recipe=self.recipe,
            comment_text='Коммент для удаления'
        )
        url = comment_detail_url(comment_to_delete.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=comment_to_delete.id).exists())

    def test_delete_comment_by_other_user_forbidden(self):
        """Тест: пользователь не может удалить чужой комментарий"""
        url = comment_detail_url(self.comment.id)
        response = self.client.delete(url)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])


    def test_unauthenticated_user_cannot_comment(self):
        """Тест: неаутентифицированный пользователь не может комментировать"""
        self.client.force_authenticate(user=None)
        payload = {
            'recipe': self.recipe.id,
            'comment_text': 'Анонимный коммент'
        }
        response = self.client.post(COMMENTS_LIST_URL, payload)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])


    def test_get_comments_of_recipe(self):
        """Тест: Получение всех комментариев к одному рецепту"""
        self.client.force_authenticate(user=self.user1)
        response: Response = self.client.get(COMMENTS_LIST_URL + f"?recipe__id={self.recipe.id}") # noqa
        print()
        self.assertEqual(response.data[0]['recipe'], self.recipe.id)



class SearchHistoryAPITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='searcher1', password='password1')
        self.user2 = User.objects.create_user(username='searcher2', password='password2')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

        SearchHistory.objects.create(user=self.user1, text='пирог')
        SearchHistory.objects.create(user=self.user1, text='суп')
        SearchHistory.objects.create(user=self.user2, text='салат')

    def tearDown(self):
        cache.clear()

    def test_create_search_history_success(self):
        """Тест успешного создания записи истории поиска"""
        payload = {'text': 'блины'}
        response = self.client.post(SEARCH_HISTORY_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(SearchHistory.objects.filter(user=self.user1, text='блины').exists())
        print(response.data)
        self.assertEqual(response.data['data']['text'], 'блины')
        self.assertEqual(response.data['data']['user']['username'], self.user1.username)

    def test_create_search_history_missing_text(self):
        """Тест создания записи без текста"""
        payload = {}
        response = self.client.post(SEARCH_HISTORY_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('text', response.data)

    def test_list_search_history_returns_only_own(self):
        """Тест: список истории поиска возвращает только записи текущего пользователя"""
        response = self.client.get(SEARCH_HISTORY_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        texts = {item['text'] for item in response.data}
        self.assertEqual(texts, {'пирог', 'суп'})
        for item in response.data:
            self.assertEqual(item['user']['username'], self.user1.username)

    def test_unauthenticated_user_cannot_create_or_list_history(self):
        """Тест: неаутентифицированный пользователь не может работать с историей"""
        # Clear any existing cache before testing
        cache.clear()
        
        self.client.force_authenticate(user=None)

        payload = {'text': 'анонимный поиск'}
        response_post = self.client.post(SEARCH_HISTORY_LIST_URL, payload)
        self.assertIn(response_post.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

        response_get = self.client.get(SEARCH_HISTORY_LIST_URL)
        self.assertIn(response_get.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])