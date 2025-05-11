from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Course, Module, Lesson, LessonContent, UserCourseProgress, LessonCompletion
from rest_framework.exceptions import ValidationError

class LessonContentSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = LessonContent
        fields = [
            'id', 'content_type', 'type', 'title', 'text',
            'video_url', 'image', 'file', 'order',
            'code_language', 'quiz_data', 'table_data'
        ]
        extra_kwargs = {
            'content_type': {'required': True},
            'image': {'required': False, 'allow_null': True},
            'file': {'required': False, 'allow_null': True},
            'video_url': {'required': False, 'allow_null': True},
            'text': {'required': False, 'allow_null': True},
            'code_language': {'required': False, 'allow_null': True},
            'quiz_data': {'required': False, 'allow_null': True},
            'table_data': {'required': False, 'allow_null': True},
            'title': {'required': False, 'allow_null': True},
        }

    def get_type(self, obj):
        return {
            'TEXT': 'text',
            'IMAGE': 'image',
            'VIDEO': 'video',
            'FILE': 'file',
            'CODE': 'code',
            'QUIZ': 'quiz',
            'TABLE': 'table',
        }.get(obj.content_type, 'text')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        content_representation = {
            'TEXT': lambda: {'text': instance.text},
            'IMAGE': lambda: {'url': instance.image.url if instance.image else None},
            'VIDEO': lambda: {'url': instance.video_url},
            'FILE': lambda: {'url': instance.file.url if instance.file else None},
            'CODE': lambda: {
                'text': instance.text,
                'language': instance.code_language
            },
            'QUIZ': lambda: {
                'question': instance.quiz_data.get('question', ''),
                'answers': instance.quiz_data.get('answers', []),
                'correct_answer': instance.quiz_data.get('correct_answer')
            },
            'TABLE': lambda: {
                'headers': instance.table_data.get('headers', []),
                'data': instance.table_data.get('data', [])
            }
        }
        data.update(content_representation.get(instance.content_type, lambda: {})())
        return data

    def validate(self, data):
        content_type = data.get('content_type')
        if not content_type:
            raise ValidationError("Content type is required.")

        validation_rules = {
            'TEXT': {'required': ['text'], 'optional': ['title']},
            'VIDEO': {'required': ['video_url'], 'optional': ['title']},
            'IMAGE': {'required': ['image'], 'optional': ['title']},
            'FILE': {'required': ['file'], 'optional': ['title']},
            'CODE': {'required': ['text', 'code_language'], 'optional': ['title']},
            'QUIZ': {'required': ['quiz_data'], 'optional': ['title']},
            'TABLE': {'required': ['table_data'], 'optional': ['title']},
        }

        rules = validation_rules.get(content_type)
        if not rules:
            raise ValidationError(f"Invalid content type: {content_type}")

        errors = {}
        # Check required fields
        for field in rules['required']:
            if field not in data or data[field] is None:
                errors[field] = f"{field} is required for {content_type} content type."
            elif field == 'quiz_data':
                quiz_data = data.get('quiz_data', {})
                if not quiz_data.get('question'):
                    errors['quiz_data'] = "Question is required for QUIZ content type."
                if not quiz_data.get('answers') or len(quiz_data.get('answers', [])) < 2:
                    errors['quiz_data'] = "At least two answers are required for QUIZ content type."
            elif field == 'table_data':
                table_data = data.get('table_data', {})
                if not table_data.get('headers'):
                    errors['table_data'] = "Headers are required for TABLE content type."
                if not table_data.get('data'):
                    errors['table_data'] = "Data is required for TABLE content type."

        # Check that non-relevant fields are not provided
        all_fields = ['text', 'video_url', 'image', 'file', 'code_language', 'quiz_data', 'table_data']
        relevant_fields = rules['required'] + rules['optional']
        for field in all_fields:
            if field not in relevant_fields and field in data and data[field] is not None:
                errors[field] = f"{field} should not be provided for {content_type} content type."

        if errors:
            raise ValidationError(errors)

        return data


class LessonSerializer(serializers.ModelSerializer):
    contents = LessonContentSerializer(many=True, read_only=True)
    is_completed = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'order', 'thumbnail',
            'type', 'created_at', 'updated_at', 'duration', 
            'contents', 'is_completed'
        ]
        extra_kwargs = {
            'thumbnail': {'required': False, 'allow_null': True},
            'description': {'required': False, 'allow_null': True},
        }

    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return LessonCompletion.objects.filter(
                progress__user=request.user,
                progress__course=obj.module.course,
                lesson=obj,
                is_completed=True
            ).exists()
        return False

    def validate(self, data):
        module_id = self.context['view'].kwargs.get('module_id')
        if not module_id:
            raise ValidationError("Module ID is required")
        
        if 'title' in data:
            qs = Lesson.objects.filter(module_id=module_id, title=data['title'])
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError({
                    'title': 'Lesson with this title already exists in this module'
                })
        return data


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    course = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Course.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = Module
        fields = [
            'id', 'title', 'description', 
            'order', 'course', 'lessons', 
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'description': {'required': False, 'allow_null': True},
            'course': {'write_only': True}
        }

    def validate(self, data):
        course = data.get('course')
        title = data.get('title')
        if course and title:
            qs = Module.objects.filter(course=course, title=title)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError({
                    'title': 'Module with this title already exists in this course'
                })
        return data


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description',
            'author', 'thumbnail', 'is_published',
            'modules',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'thumbnail': {'required': False, 'allow_null': True},
            'description': {'required': False, 'allow_null': True},
            'author': {'read_only': True},
            'slug': {'read_only': True},
        }

    def get_user_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            progress = UserCourseProgress.objects.filter(
                user=request.user,
                course=obj
            ).first()
            if progress:
                return UserCourseProgressSerializer(progress, context=self.context).data
        return None
    

class LessonCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonCompletion
        fields = ['id', 'lesson', 'is_completed', 'completed_at', 'last_accessed', 'score']
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['lesson'] = {
            'id': instance.lesson.id,
            'title': instance.lesson.title,
            'module_id': instance.lesson.module.id
        }
        return data


class UserCourseProgressSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = UserCourseProgress
        fields = [
            'id', 'started_at', 'last_accessed', 'is_completed', 'completed_at',
            'course', 'progress'
        ]
        read_only_fields = fields

    def get_course(self, obj):
        return {
            'id': obj.course.id,
            'title': obj.course.title,
            'slug': obj.course.slug,
            'thumbnail': obj.course.thumbnail.url if obj.course.thumbnail else None
        }

    def get_progress(self, obj):
        total = Lesson.objects.filter(module__course=obj.course).count()
        completed = obj.completed_lessons.filter(is_completed=True).count()
        return {
            'completed': completed,
            'total': total,
            'percentage': round((completed / total) * 100) if total > 0 else 0
        }