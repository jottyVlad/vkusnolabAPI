from django.contrib.auth.models import AbstractUser
from django.db import models

from baseAPI import settings


class CustomUser(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    #TODO: разобраться что за путь к картинке
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    registered_on = models.DateTimeField(auto_now_add=True)


class Followers(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    author_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user_id', 'author_id'], name='unique_followers'
            )
        ]