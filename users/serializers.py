from django.contrib.auth import get_user_model
from rest_framework import serializers

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'email': {'required': True},
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        if get_user_model().objects.filter(email=attrs['email']).exists() or get_user_model().objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError("This email or username is already in use.")

        return attrs

    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password', 'bio', 'profile_picture']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'bio', 'profile_picture']