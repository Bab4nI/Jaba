from rest_framework import viewsets, permissions
from .models import Course, Module, Lesson, LessonContent
from .serializers import CourseSerializer, ModuleSerializer, LessonSerializer, LessonContentSerializer
from django.shortcuts import get_object_or_404


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseSerializer
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

class ModuleViewSet(viewsets.ModelViewSet):
    serializer_class = ModuleSerializer
    
    def get_queryset(self):
        return Module.objects.filter(
            course__slug=self.kwargs['course_slug'],
            course__is_published=True
        )
    
    def perform_create(self, serializer):
        # Получаем курс по slug из URL
        course = get_object_or_404(Course, slug=self.kwargs['course_slug'])
        # Сохраняем модуль с привязкой к курсу
        serializer.save(course=course)

from rest_framework.parsers import MultiPartParser, FormParser

class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    parser_classes = [MultiPartParser, FormParser]  # Для загрузки файлов
    
    def get_queryset(self): 
        return Lesson.objects.filter(
            module__id=self.kwargs['module_id'], 
            module__course__is_published=True
        )
    
    def perform_create(self, serializer):
        module = get_object_or_404(Module, id=self.kwargs['module_id'])
        serializer.save(module=module)

class LessonContentViewSet(viewsets.ModelViewSet):
    serializer_class = LessonContentSerializer
    parser_classes = [MultiPartParser, FormParser]  # Для загрузки файлов
    
    def get_queryset(self):
        return LessonContent.objects.filter(
            lesson__id=self.kwargs['lesson_id'],
            lesson__module__course__is_published=True
        )
    
    def perform_create(self, serializer):
        lesson = get_object_or_404(Lesson, id=self.kwargs['lesson_id'])
        serializer.save(lesson=lesson) 