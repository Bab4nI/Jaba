# user_profile/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()

class GetUserProfileView(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        # Получаем пользователя из запроса (автоматически через JWT)
        user = request.user

        # Формируем данные для ответа
        data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'middle_name': user.middle_name,
            'email': user.email,
            'group': user.group,
            'avatar_base64': user.avatar_base64,
            'role': user.role
        }
        return Response(data)

    def patch(self, request):
        user = request.user
        data = request.data

        # Обновляем поля пользователя
        user.email = data.get('email', user.email)
        user.avatar_base64 = data.get('avatar_base64', user.avatar_base64)
        user.save()

        return Response(status=status.HTTP_200_OK)
