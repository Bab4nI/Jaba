from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Content, CustomForm
from .serializers import ContentSerializer, CustomFormSerializer
from progress.models import ContentProgress
from courses.models import Lesson
from django.core.exceptions import ValidationError

# Create your views here.

class ContentViewSet(viewsets.ModelViewSet):
    serializer_class = ContentSerializer
    permission_classes = [AllowAny]  # Allow read access to everyone

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'submit_answer', 'reorder']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        lesson_id = self.request.query_params.get('lesson_id')
        if lesson_id:
            return Content.objects.filter(lesson_id=lesson_id)
        return Content.objects.all()

    def perform_create(self, serializer):
        lesson_id = self.request.data.get('lesson_id')
        if not lesson_id:
            raise ValidationError({'lesson_id': 'This field is required'})
        lesson = get_object_or_404(Lesson, id=lesson_id)
        serializer.save(lesson=lesson)

    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        content = self.get_object()
        score = request.data.get('score', 0)
        user_answer = request.data.get('user_answer', {})

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
    def reorder(self, request):
        order_data = request.data.get('order', [])
        
        for item in order_data:
            content = get_object_or_404(Content, id=item['id'])
            content.order = item['order']
            content.save()

        return Response({'status': 'success'})

class CustomFormViewSet(viewsets.ModelViewSet):
    serializer_class = CustomFormSerializer
    permission_classes = [AllowAny]  # Allow read access to everyone

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'add_content', 'remove_content']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        lesson_id = self.request.query_params.get('lesson_id')
        if lesson_id:
            return CustomForm.objects.filter(lesson_id=lesson_id)
        return CustomForm.objects.all()

    def perform_create(self, serializer):
        lesson_id = self.request.data.get('lesson_id')
        if not lesson_id:
            raise ValidationError({'lesson_id': 'This field is required'})
        lesson = get_object_or_404(Lesson, id=lesson_id)
        serializer.save(lesson=lesson)

    @action(detail=True, methods=['get'])
    def contents(self, request, pk=None):
        form = self.get_object()
        related_contents = form.contents.all().order_by('order')
        if related_contents.exists():
            contents = related_contents
        else:
            # Если нет связанных элементов, вернуть все элементы урока
            contents = Content.objects.filter(lesson=form.lesson).order_by('order')
        serializer = ContentSerializer(contents, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_content(self, request, pk=None):
        form = self.get_object()
        content_id = request.data.get('content_id')
        order = request.data.get('order', 0)
        
        if not content_id:
            return Response(
                {'error': 'content_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        content = get_object_or_404(Content, id=content_id)
        
        # Update content order
        content.order = order
        content.save()
        
        # Add content to form
        form.contents.add(content)
        
        return Response({'status': 'success'})

    @action(detail=True, methods=['post'])
    def remove_content(self, request, pk=None):
        form = self.get_object()
        content_id = request.data.get('content_id')
        
        if not content_id:
            return Response(
                {'error': 'content_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        content = get_object_or_404(Content, id=content_id)
        form.contents.remove(content)
        
        return Response({'status': 'success'})
