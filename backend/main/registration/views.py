import json
from urllib.parse import urlencode
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import send_mail

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import CustomTokenObtainPairSerializer, UserSerializer
from .models import User

# Словарь с текстами ошибок
ERROR_RESPONSES = {
    400: {"error": "Некорректный запрос", "details": "Проверьте предоставленные данные."},
    404: {"error": "Страница не существует", "details": "Запрашиваемый ресурс не найден."},
    500: {"error": "Ошибка сервера", "details": "Произошла внутренняя ошибка сервера."},
    "missing_field": {"error": "Недостающее поле", "details": "Поле '{}' обязательно для заполнения."},
    "invalid_json": {"error": "Некорректный JSON", "details": "Тело запроса содержит некорректный JSON."},
    "email_send_failed": {"error": "Ошибка отправки email", "details": "Не удалось отправить email: {}."},
    "user_not_found": {"error": "Пользователь не найден", "details": "Пользователь с ID {} не существует."},
    "invalid_data": {"error": "Некорректные данные", "details": "Проверьте предоставленные данные."},
}

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class SendRegistrationLinkView(APIView):
    def post(self, request):
        try:
            data = request.data
            
            required_fields = ['last_name', 'first_name', 'middle_name', 'email', 'role']
            for field in required_fields:
                if field not in data:
                    error_response = ERROR_RESPONSES["missing_field"]
                    error_response["details"] = error_response["details"].format(field)
                    return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

            # Создание токена с данными пользователя
            payload = {
                'last_name': data['last_name'],
                'first_name': data['first_name'],
                'middle_name': data['middle_name'],
                'email': data['email'],
                'group': data.get('group', ''),
                'role': data['role'],
                'exp': datetime.utcnow() + timedelta(minutes=15)  # токен истекает через 15 минут
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

            # Создание защищённой ссылки с токеном
            registration_url = f'http://localhost:5173/SignUp?token={token}'

            # Отправка email
            subject = 'Завершите регистрацию в NetLab AI'
            message = f'''Здравствуйте, {data['first_name']}!
            
Для завершения регистрации перейдите по ссылке:
{registration_url}

После перехода по ссылке вам останется только ввести пароль.
'''
            send_mail(
                subject,
                message,
                'sfedu.netlabai@gmail.com',
                [data['email']],
                fail_silently=False,
            )

            return Response({"status": "Email sent successfully"})

        except Exception as e:
            error_response = ERROR_RESPONSES["email_send_failed"]
            error_response["details"] = error_response["details"].format(str(e))
            return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserListView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class RegisterView(APIView):    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)