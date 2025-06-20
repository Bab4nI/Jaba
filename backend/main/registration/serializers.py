# registration/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            email=email, password=password
        )  # Используем стандартный метод

        if user is None:
            raise serializers.ValidationError({"error": "Неверный email или пароль"})

        # Генерируем токены
        refresh = self.get_token(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "group": {"required": False},  # Делаем поле group необязательным
            "password": {"write_only": True},  # Ensure password is write-only
        }

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        # Mark that we're explicitly setting the role
        role = validated_data.get("role")

        user = User(**validated_data)
        # Set a flag to indicate role was explicitly provided
        if role:
            user._role_explicitly_set = True

        if password:
            user.set_password(password)  # Используем встроенный метод

        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(min_length=8, required=True)


class ChangeEmailRequestSerializer(serializers.Serializer):
    new_email = serializers.EmailField(required=True)


class VerifyEmailCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, required=True)
