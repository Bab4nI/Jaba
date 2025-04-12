from rest_framework import serializers
from .models import Course, Module, Lesson, LessonContent



class LessonContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonContent
        fields = [
            'id', 'content_type', 'title', 'text', 
            'video_url', 'image', 'gif', 'file', 'order'
        ]
        extra_kwargs = {
            'image': {'required': False, 'allow_null': True},
            'gif': {'required': False, 'allow_null': True},
            'file': {'required': False, 'allow_null': True},
            'video_url': {'required': False, 'allow_null': True},
            'text': {'required': False, 'allow_null': True}
        }

class LessonSerializer(serializers.ModelSerializer):
    contents = LessonContentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'duration', 'thumbnail',
            'order', 'contents', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'thumbnail': {'required': False}, 
        }

class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    
    class Meta:
        model = Module
        fields = [
            'id', 'title', 'description', 
            'order', 'lessons'
        ]

class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description',
            'author', 'thumbnail', 'is_published',
            'modules', 'created_at'
        ]
