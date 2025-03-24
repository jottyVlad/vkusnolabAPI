from rest_framework import serializers

from users.models import CustomUser as User


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password"]
        extra_kwargs = {"email": {"required": True}, "password": {"write_only": True}}

    def validate(self, attrs):
        if (
            User.objects.filter(email=attrs["email"]).exists()
            or User.objects.filter(username=attrs["username"]).exists()
        ):
            raise serializers.ValidationError(
                "This email or username is already in use."
            )

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user
