from django.utils import timezone
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APITestCase
from django.core.cache import cache
from chatAI.models import ChatHistory
from users.models import CustomUser


class ChatHistoryAPITests(APITestCase):
    def setUp(self):
        cache.clear()
        self.user = CustomUser.objects.create_user(
            username='test',
            email='test@example.com',
            bio='Это тестовая биография пользователя.',
            profile_picture='profile_pics/test.png',
            registered_on=timezone.now()
        )

        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

        message = ChatHistory(
            text="Привет, пользователь!",
            user=self.user,
            created_at=timezone.now(),
            sender_type="AI"
        )
        message.save()

        another_message = ChatHistory(
            text="Привет, я ИИ!",
            user=self.user,
            created_at=timezone.now(),
            sender_type="AI"
        )
        another_message.save()

        user_message = ChatHistory(
            text="Приивееет",
            user=self.user,
            created_at=timezone.now(),
            sender_type="user"
        )
        user_message.save()

    def tearDown(self):
        cache.clear()

    def test_get_code_200(self):
        """Тест на получения кода 200"""
        response = self.client.get("/api/v1/chat/chat_history/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_message(self):
        data = {
            "user_id": self.user.id,
            "text": "Привет, привет, рад тебя видеть",
            "sender_type": "user"
        }

        response = self.client.post(
            "/api/v1/chat/chat_history/",
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['text'], data['text'])
        self.assertEqual(response.data['data']['sender_type'], data['sender_type'])

        self.assertEqual(ChatHistory.objects.filter(text=data["text"]).count(), 1)

    def test_get_message_ai(self):
        """Тест получения списка сообщений от AI"""
        response = self.client.get("/api/v1/chat/chat_history/ai_messages/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ChatHistory.objects.count(), 3)
        self.assertEqual(len(response.data), 2)

    def test_clear_history(self):
        """Тест очистки истории чатов"""
        cache.clear()  # Clear cache before testing
        response = self.client.get("/api/v1/chat/chat_history/clear_history/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ChatHistory.objects.count(), 0)