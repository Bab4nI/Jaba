import json
from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlencode
from django.views.decorators.http import require_http_methods
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import UserSerializer
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

@csrf_exempt
@require_http_methods(["GET", "POST"])
def send_registration_link(request):
    if request.method == 'GET':
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

    elif request.method == 'POST':
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

@api_view(['GET', 'POST'])
def user_list(request):
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {"error": ERROR_RESPONSES["invalid_data"]["error"], "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        error_response = ERROR_RESPONSES["user_not_found"]
        error_response["details"] = error_response["details"].format(pk)
        return Response(error_response, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            {"error": ERROR_RESPONSES["invalid_data"]["error"], "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)