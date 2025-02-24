# views.py
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


@csrf_exempt
@require_http_methods(["GET", "POST"])  # Разрешаем GET и POST запросы
def send_registration_link(request):
    if request.method == 'GET':
        # Возвращаем JSON для GET-запроса
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
        # Обработка POST-запроса (ваш существующий код)
        try:
            data = json.loads(request.body)
            
            # Валидация обязательных полей
            required_fields = ['last_name', 'first_name', 'email', 'group']
            for field in required_fields:
                if field not in data:
                    return JsonResponse(
                        {'error': f'Missing required field: {field}'},
                        status=400
                    )

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

            return JsonResponse({'status': 'Email sent successfully'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)