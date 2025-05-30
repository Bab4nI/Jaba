from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import ContentProgress
from content.models import Content
from courses.models import Lesson
from .serializers import ContentProgressSerializer

class ContentProgressViewSet(viewsets.ModelViewSet):
    serializer_class = ContentProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ContentProgress.objects.filter(user=self.request.user)
        lesson_id = self.request.query_params.get('lesson_id')
        if lesson_id:
            queryset = queryset.filter(content__lesson_id=lesson_id)
        return queryset

    @action(detail=False, methods=['post'])
    def update_progress(self, request):
        content_id = request.data.get('content_id')
        score = request.data.get('score', 0)
        user_answer = request.data.get('user_answer', {})

        if not content_id:
            return Response(
                {'error': 'content_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        content = get_object_or_404(Content, id=content_id)
        
        progress, created = ContentProgress.objects.get_or_create(
            user=request.user,
            content=content,
            defaults={'score': score, 'user_answer': user_answer}
        )

        if not created:
            progress.score = score
            progress.user_answer = user_answer
            progress.save()

        return Response({
            'score': progress.score,
            'completed': progress.completed
        })

    @action(detail=False, methods=['post'])
    def reset_progress(self, request):
        lesson_id = request.data.get('lesson_id')
        
        if not lesson_id:
            return Response(
                {'error': 'lesson_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        lesson = get_object_or_404(Lesson, id=lesson_id)
        contents = Content.objects.filter(lesson=lesson)
        
        # Delete all progress for this lesson's contents
        ContentProgress.objects.filter(
            user=request.user,
            content__in=contents
        ).delete()

        return Response({'status': 'success'}) 