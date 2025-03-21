from django.db import models
from django.conf import settings

class ChatHistory(models.Model):
    text = models.CharField(max_length=5000)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Связь с пользователем
    created_at = models.DateTimeField(auto_now_add=True)
    sender_type = models.CharField(max_length=5)
