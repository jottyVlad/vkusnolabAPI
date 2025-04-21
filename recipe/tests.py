from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APITestCase
from recipe.models import Recipe
from users.models import CustomUser


class RecipeViewSetAPTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='test',
            email='test@example.com',
            bio='Это тестовая биография пользователя.',
            profile_picture='test.png',
            registered_on=timezone.now()
        )

        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        recipe = Recipe(
            author_id=self.user,
            title="Спагетти Карбонара",
            description="Классический итальянский рецепт пасты с соусом из яиц, сыра пармезан и гуанчиале",
            instructions="1. Отварите спагетти в подсоленной воде...",
            cooking_time_minutes=25,
            servings=4,
            image='recipe.png',
            is_active=True,
            is_private=False
            # created_at и updated_at заполнятся автоматически
        )
        recipe.save()


    def test_get_code_200(self):
        """Тест на получения кода 200"""
        response = self.client.get("/api/v1/recipe/recipe/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_get_list_of_recipes(self):
        """Тест на получение списка рецептов"""
        response = self.client.get("/api/v1/recipe/recipe/")
        self.assertEqual(response.data['count'], 1)


    def test_create_recipe(self):
        data = {
            "title": "Тестовый рецепт",
            "description": "Тестовое описание рецепта",
            "instructions": "Шаг 1. Сделать тест",
            "cooking_time_minutes": 30,
            "servings": 4
        }

        response = self.client.post(
            "/api/v1/recipe/recipe/",
            data,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверка данных в ответе
        response_data = response.data['data']
        self.assertEqual(response_data['title'], data['title'])
        self.assertEqual(response_data['description'], data['description'])
        self.assertEqual(response_data['instructions'], data['instructions'])
        self.assertEqual(response_data['cooking_time_minutes'], data['cooking_time_minutes'])
        self.assertEqual(response_data['servings'], data['servings'])

        # Проверка автора
        self.assertEqual(response_data['author_id'], self.user.id)

        # Проверка записи в базе
        self.assertEqual(Recipe.objects.count(), 2)
        recipe = Recipe.objects.all()[1]
        self.assertEqual(recipe.title, data['title'])
        self.assertEqual(recipe.author_id, self.user)  # author_id - ForeignKey


    def test_get_single_recipe(self):
        """Тест получения конкретного рецепта (GET by ID)"""
        recipe = Recipe.objects.first()
        response = self.client.get(f"/api/v1/recipe/recipe/{recipe.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Спагетти Карбонара")
        self.assertEqual(response.data['author_id'], self.user.id)


    def test_full_update_recipe_put(self):
        """Тест полного обновления рецепта (PUT)"""
        recipe = Recipe.objects.first()

        update_data = {
            "title": "Обновленные спагетти",
            "description": "Новое описание",
            "instructions": "Обновленные инструкции",
            "cooking_time_minutes": 35,
            "servings": 2,
            "is_private": True,
            "image": recipe.image
        }

        response = self.client.put(
            f"/api/v1/recipe/recipe/{recipe.id}/",
            data=update_data,
            format='multipart'  # Используйте multipart для файловых полей
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, "Обновленные спагетти")
        self.assertEqual(recipe.is_private, True)


    def test_delete_recipe(self):
        """Тест удаления рецепта (DELETE)"""
        recipe = Recipe.objects.first()
        response = self.client.delete(f"/api/v1/recipe/recipe/{recipe.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Recipe.objects.count(), 0)


    def test_foreign_user_update_permission(self):
        """Тест прав доступа для чужого пользователя"""
        # Создаем второго пользователя
        other_user = CustomUser.objects.create_user(
            username='hacker',
            email='hacker@example.com',
            password='hackpass'
        )
        refresh = RefreshToken.for_user(other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        recipe = Recipe.objects.first()

        # Пытаемся обновить чужой рецепт (передаем ВСЕ обязательные поля для PUT)
        update_data = {
            "title": "Взломанный рецепт",
            "description": recipe.description,  # обязательное поле
            "instructions": recipe.instructions,  # обязательное поле
            "cooking_time_minutes": recipe.cooking_time_minutes,
            "servings": recipe.servings
        }

        response_put = self.client.put(
            f"/api/v1/recipe/recipe/{recipe.id}/",
            update_data,  # используем полные данные
            format='json'
        )
        self.assertEqual(response_put.status_code, status.HTTP_403_FORBIDDEN)

        # Пытаемся удалить чужой рецепт
        response_delete = self.client.delete(f"/api/v1/recipe/recipe/{recipe.id}/")
        self.assertEqual(response_delete.status_code, status.HTTP_403_FORBIDDEN)


    def test_invalid_data_update(self):
        """Тест валидации неверных данных при обновлении"""
        recipe = Recipe.objects.first()
        invalid_data = {
            "cooking_time_minutes": -10,
            "servings": 0
        }

        response = self.client.patch(
            f"/api/v1/recipe/recipe/{recipe.id}/",
            invalid_data,
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cooking_time_minutes', response.data)
        self.assertIn('servings', response.data)


    def test_nonexistent_recipe(self):
        """Тест обращения к несуществующему рецепту"""
        response = self.client.get("/api/v1/recipe/recipe/9999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.delete("/api/v1/recipe/recipe/9999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)