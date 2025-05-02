from rest_framework import serializers
from django.contrib.auth import get_user_model

from chatAI.models import ChatHistory


class ChatHistorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для истории чата с ИИ помощником.

    Обрабатывает создание и отображение записей чата между пользователем и ИИ.
    Автоматически устанавливает:
    - Дату создания записи (created_at)
    - Связь с пользователем (user_id)

    Поля:
    - text: текст сообщения (макс. 5000 символов)
    - sender_type: тип отправителя ('user' или 'AI')
    - created_at: дата создания записи (только чтение)
    """
    User = get_user_model()
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        help_text="ID пользователя, связанного с историей чата"
    )

    class Meta:
        model = ChatHistory
        fields = '__all__'
        extra_kwargs = {
            'text': {
                'max_length': 5000,
                'help_text': "Текст сообщения (максимум 5000 символов)"
            },
            'created_at': {
                'read_only': True,
                'help_text': "Дата создания записи (автоматически устанавливается)"
            },
            'sender_type': {
                'max_length': 5,
                'help_text': "Тип отправителя: 'user' или 'AI'"
            },
        }

    def validate(self, value):
        """Проверяет корректность типа отправителя.

        Args: value (str): Значение поля sender_type
        Returns: str: Проверенное значение
        Raises: serializers.ValidationError: Если значение не 'user' или не 'AI'
        """
        allowed_values = ['user', 'AI']
        if value['sender_type'] not in allowed_values:
            raise serializers.ValidationError(
                f"Тип отправителя должен быть одним из: {', '.join(allowed_values)}"
            )
        return value


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        exclude = ('user',)

    def save(self, **kwargs):
        raise NotImplementedError("You cannot use save method for this serializer")
