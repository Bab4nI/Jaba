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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Определяем роль, если не задана явно
        role = getattr(user, 'role', None)
        if not role:
            if getattr(user, 'is_superuser', False):
                role = 'admin'
            elif getattr(user, 'is_staff', False):
                role = 'teacher'
            else:
                role = 'student'

        # Add debug logging
        print(f"User profile request for {user.email}, role in DB: {role}, is_staff: {user.is_staff}")

        # Формируем данные для ответа
        data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'middle_name': user.middle_name,
            'email': user.email,
            'group': user.group,
            'avatar_base64': user.avatar_base64,
            'role': role,
            'is_staff': user.is_staff,  # Adding this to help with debugging
            'id': user.id,  # Adding this to help with debugging
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

class GroupUsersView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        group = request.query_params.get('group')
        if not group:
            return Response({'error': 'group parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        users = User.objects.filter(group=group, role='student')
        data = [
            {
                'id': user.id,
                'full_name': f"{user.last_name} {user.first_name} {user.middle_name}".strip(),
                'first_name': user.first_name,
                'last_name': user.last_name,
                'middle_name': user.middle_name,
                'email': user.email,
                'group': user.group
            }
            for user in users
        ]
        return Response(data)

class AdminsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        admins = User.objects.filter(role='admin')
        data = [
            {
                'id': user.id,
                'full_name': f"{user.last_name} {user.first_name} {user.middle_name}".strip(),
                'first_name': user.first_name,
                'last_name': user.last_name,
                'middle_name': user.middle_name,
                'email': user.email,
                'group': user.group
            }
            for user in admins
        ]
        return Response(data)

class GroupsListView(APIView):
    """
    API endpoint to get the unique list of groups from all users
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch all unique groups from users, excluding empty ones
        groups = User.objects.filter(group__isnull=False).exclude(group='').values_list('group', flat=True).distinct()
        
        # Return as a simple list
        return Response(list(groups))
