from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, get_user_model
from django.core.files.base import ContentFile
import base64

User = get_user_model()
class GetUserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
       user = request.user
       data = {
           'first_name': user.first_name,
           'last_name': user.last_name,
           'middle_name': user.middle_name,
           'email': user.email,
           'group': user.group,
           'level': user.level,
           'department': user.department,
           'avatar_base64': user.avatar_base64,  # Добавляем аватарку в ответ
       }
       return Response(data)
    
    def patch(self, request):
        user = request.user
        data = request.data
        
        user.email = data.get('email', user.email)
        user.avatar_base64 = data.get('avatar_base64', user.avatar_base64)
        user.save()
        return Response(status=status.HTTP_200_OK)