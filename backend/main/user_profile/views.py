from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

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
            'course': user.course,
            'department': user.department,
        }
        return Response(data)