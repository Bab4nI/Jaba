import json
from urllib.parse import urlencode

from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import CustomTokenObtainPairSerializer, UserSerializer
from .models import User


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

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

@csrf_exempt
@require_http_methods(["GET", "POST"])
def send_registration_link(request):  # /api/send-registration-link
    if request.method == 'GET':       # логика для get
        response_data = {
            "message": "Это GET-запрос. Используйте POST для отправки данных.",
            "example_request": {
                "last_name": "Иванов",
                "first_name": "Иван",
                "email": "user@example.com",
                "group": "АИ-21"
            },
            "example_response": {
                "status": "Email sent successfully"
            }
        }
        return JsonResponse(response_data)

    elif request.method == 'POST':  #логика для post
        try:
            data = json.loads(request.body)
            
            # Валидация обязательных полей
            required_fields = ['last_name', 'first_name', 'email', 'group']
            for field in required_fields:
                if field not in data:
                    error_response = ERROR_RESPONSES["missing_field"]
                    error_response["details"] = error_response["details"].format(field)
                    return JsonResponse(error_response, status=400)

            # Создание URL с предзаполненными данными
            params = {
                'last_name': data['last_name'],
                'first_name': data['first_name'],
                'email': data['email'],
                'group': data['group']
            }
            encoded_params = urlencode(params)
            registration_url = f'http://localhost:5173/SignUp?{encoded_params}'

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
                'noreply@netlab.ai',  # Замените на ваш email
                [data['email']],
                fail_silently=False,
            )

            return JsonResponse({"status": "Email sent successfully"})

        except json.JSONDecodeError:
            return JsonResponse(ERROR_RESPONSES["invalid_json"], status=400)
        except Exception as e:
            error_response = ERROR_RESPONSES["email_send_failed"]
            error_response["details"] = error_response["details"].format(str(e))
            return JsonResponse(error_response, status=500)

@api_view(['GET'])
def user_list(request):
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'group': user.group,
        'level': user.level,
        'course': user.course,
        'department': user.department,
    }
    return Response(data)

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserByEmailView(APIView):
    permission_classes = [IsAuthenticated]  # Только для аутентифицированных пользователей

    def get(self, request):
        """
        Получение пользователя по email.
        """
        email = request.query_params.get('email')
        if not email:
            return Response({"error": "Параметр 'email' обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "Пользователь с таким email не найден"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        """
        Обновление пользователя по email.
        """
        email = request.query_params.get('email')
        if not email:
            return Response({"error": "Параметр 'email' обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Пользователь с таким email не найден"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """
        Удаление пользователя по email.
        """
        email = request.query_params.get('email')
        if not email:
            return Response({"error": "Параметр 'email' обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            user.delete()
            return Response({"status": "Пользователь успешно удален"}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"error": "Пользователь с таким email не найден"}, status=status.HTTP_404_NOT_FOUND)