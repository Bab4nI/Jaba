import jwt
from datetime import datetime, timedelta
import random
import logging

from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string, get_template
from django.utils.html import strip_tags
from django.contrib.auth.hashers import make_password, check_password

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.state import token_backend
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, UntypedToken

from .serializers import (
    CustomTokenObtainPairSerializer, 
    UserSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    ChangeEmailRequestSerializer,
    VerifyEmailCodeSerializer,
)
from .models import User

logger = logging.getLogger(__name__)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class SendRegistrationLinkView(APIView):
    def post(self, request):
        try:
            data = request.data
            required_fields = ['last_name', 'first_name', 'email', 'role']
            for field in required_fields:
                if field not in data:
                    return Response(
                        {"error": f"Поле '{field}' обязательно"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            payload = {
                'last_name': data['last_name'],
                'first_name': data['first_name'],
                'middle_name': data.get('middle_name', ''),
                'email': data['email'],
                'group': data.get('group', ''),
                'role': data['role'],
                'exp': datetime.utcnow() + timedelta(minutes=15)
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
            registration_url = f'{frontend_url}/SignUp?token={token}'
            
            context = {
                'first_name': data['first_name'],
                'registration_url': registration_url,
            }
            
            subject = 'Завершите регистрацию в NetLab AI'
            html_message = render_to_string('registration/registration_email.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [data['email']],
                html_message=html_message,
                fail_silently=False,
            )
            return Response({"status": "Email отправлен"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Ошибка отправки email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserListView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class RegisterView(APIView):    
    def post(self, request):
        # Make a copy of the data to prevent modifying the original
        data = request.data.copy()
        role = data.get('role')
        
        # Log the incoming registration data (without password)
        log_data = {k: v for k, v in data.items() if k != 'password'}
        logger.info(f"Registration attempt with data: {log_data}")
        
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            # If role is admin, make sure we're handling it
            if role == 'admin':
                logger.info(f"Creating admin user for {data.get('email')}")
                # Set group to 'admins' for admin users
                data['group'] = 'admins'
            
            user = serializer.save()
            logger.info(f"User created with ID {user.id}, role: {user.role}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        logger.warning(f"Registration failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"status": "Если пользователь существует, ссылка будет отправлена"},
                status=status.HTTP_200_OK
            )
        
        # Генерируем токен сброса с коротким сроком жизни
        token = RefreshToken.for_user(user)
        token.set_exp(lifetime=timedelta(hours=1))
        
        # Добавляем email в payload для удобства
        token['email'] = user.email
        
        reset_url = f"{settings.FRONTEND_URL}/New_password?token={str(token.access_token)}"
        
        # Отправка email
        context = {
            'user': user,
            'reset_url': reset_url,
            'site_name': 'NetLab AI'
        }
        
        try:
            html_message = render_to_string('registration/password_reset_e.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                'Сброс пароля для NetLab AI',
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                html_message=html_message,
            )
            return Response(
                {"status": "Если пользователь существует, ссылка будет отправлена"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print(f"Email sending error: {e}")
            return Response(
                {"error": f"Ошибка при отправке email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            # Декодируем токен без проверки типа
            untyped_token = UntypedToken(token)
            
            # Проверяем подпись и срок действия
            try:
                token_backend.decode(token, verify=True)
            except TokenError as e:
                raise InvalidToken(str(e))
            
            # Получаем данные из токена
            token_data = untyped_token.payload
            user = User.objects.get(email=token_data['email'])
            
            # Устанавливаем новый пароль
            user.set_password(new_password)
            user.save()
            
            # Инвалидируем токен (если нужно)
            try:
                from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
                BlacklistedToken.objects.create(token=token)
            except Exception as e:
                print(f"Couldn't blacklist token: {e}")
            
            return Response(
                {"status": "Пароль успешно изменен"},
                status=status.HTTP_200_OK
            )
            
        except InvalidToken as e:
            print(f"Invalid token: {e}")
            return Response(
                {"error": "Недействительный или просроченный токен"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Unexpected error: {e}")
            return Response(
                {"error": "Ошибка при сбросе пароля"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class ChangeEmailRequestView(APIView):
    def post(self, request):
        serializer = ChangeEmailRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        new_email = serializer.validated_data['new_email']
        user = request.user
        
        # Проверка что email не занят
        if User.objects.filter(email=new_email).exists():
            return Response(
                {"error": "Этот email уже используется"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Генерация кода подтверждения
        verification_code = str(random.randint(100000, 999999))
        user.new_email = new_email
        user.email_verification_code = verification_code
        user.email_verification_code_expires = timezone.now() + timedelta(minutes=15)
        user.save()
        
        # Отправка кода на новый email
        context = {
            'code': verification_code,
            'site_name': 'NetLab AI'
        }
        
        try:
            subject = 'Подтверждение смены email'
            html_message = render_to_string('registration/email_verification.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [new_email],
                html_message=html_message,
            )
            return Response(
                {"status": "Код подтверждения отправлен на новый email"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print(f"Email sending error: {e}")
            return Response(
                {"error": f"Ошибка при отправке кода подтверждения: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VerifyEmailCodeView(APIView):
    def post(self, request):
        serializer = VerifyEmailCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        code = serializer.validated_data['code']
        user = request.user
        
        # Проверка кода
        if (not user.email_verification_code or 
            user.email_verification_code != code or
            user.email_verification_code_expires < timezone.now()):
            return Response(
                {"error": "Неверный или просроченный код подтверждения"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Обновляем email
        user.email = user.new_email
        user.new_email = None
        user.email_verification_code = None
        user.email_verification_code_expires = None
        user.save()
        
        return Response(
            {"status": "Email успешно изменен"},
            status=status.HTTP_200_OK
        )

class UpdateAdminGroupsView(APIView):
    def post(self, request):
        try:
            # Get all users with role 'admin'
            admin_users = User.objects.filter(role='admin')
            updated_count = 0
            
            for user in admin_users:
                if user.group != 'admins':
                    user.group = 'admins'
                    user.save()
                    updated_count += 1
            
            return Response({
                "status": "success",
                "message": f"Updated {updated_count} admin users",
                "total_admins": admin_users.count()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating admin groups: {str(e)}")
            return Response(
                {"error": f"Failed to update admin groups: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )