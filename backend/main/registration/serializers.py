from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'last_name', 'first_name', 'email', 'group', 'password', 'department', 'level', 'course']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Извлекаем пароль из данных
        password = validated_data.pop('password', None)
        # Создаем пользователя
        user = User(**validated_data)
        if password:
            user.set_password(password)  # Хешируем пароль
        user.save()
        return user