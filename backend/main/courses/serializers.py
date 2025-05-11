from rest_framework import serializers
from .models import Course, Module, Lesson, LessonContent, Comment, CommentReaction
from rest_framework.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

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
        type_map = {
            'TEXT': 'text',
            'IMAGE': 'image',
            'VIDEO': 'video',
            'FILE': 'file',
            'CODE': 'code',
            'QUIZ': 'quiz',
            'TABLE': 'table',
        }
        return type_map.get(obj.content_type, 'text')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.content_type == 'TEXT':
            data['text'] = instance.text
        elif instance.content_type == 'IMAGE':
            data['url'] = instance.image.url if instance.image else None
        elif instance.content_type == 'VIDEO':
            data['url'] = instance.video_url
        elif instance.content_type == 'FILE':
            data['url'] = instance.file.url if instance.file else None
        elif instance.content_type == 'CODE':
            data['text'] = instance.text
            data['language'] = instance.code_language
        elif instance.content_type == 'QUIZ':
            data['question'] = instance.quiz_data.get('question', '')
            data['answers'] = instance.quiz_data.get('answers', [])
            data['correct_answer'] = instance.quiz_data.get('correct_answer')
        elif instance.content_type == 'TABLE':
            data['headers'] = instance.table_data.get('headers', [])
            data['data'] = instance.table_data.get('data', [])
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
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'order', 'thumbnail',
            'type', 'created_at', 'updated_at', 'duration', 'contents'
        ]
        extra_kwargs = {
            'thumbnail': {'required': False, 'allow_null': True},
            'description': {'required': False, 'allow_null': True},
            'type': {'required': True},
        }

    def validate(self, data):
        module_id = self.context['view'].kwargs.get('module_id')
        if not module_id:
            raise serializers.ValidationError("Module ID is required")
        
        if 'title' in data:
            qs = Lesson.objects.filter(module_id=module_id, title=data['title'])
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError({
                    'title': 'Урок с таким названием уже существует в этом модуле'
                })
        return data

    def create(self, validated_data):
        module_id = self.context['view'].kwargs['module_id']
        validated_data['module_id'] = module_id
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        thumbnail = validated_data.pop('thumbnail', None)
        
        if thumbnail is not None:
            if thumbnail == '':
                instance.thumbnail.delete(save=False)
                instance.thumbnail = None
            else:
                instance.thumbnail = thumbnail
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance

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
                    'title': 'Модуль с таким названием уже существует в этом курсе'
                })
        return data

class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description',
            'author', 'thumbnail', 'is_published',
            'modules', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'thumbnail': {'required': False, 'allow_null': True},
            'description': {'required': False, 'allow_null': True},
            'author': {'read_only': True},
            'slug': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

class CommentReactionSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = CommentReaction
        fields = ['id', 'user', 'reaction_type', 'created_at']

    def get_user(self, obj):
        avatar_url = None
        if hasattr(obj.user, 'avatar_base64') and obj.user.avatar_base64:
            avatar_url = obj.user.avatar_base64
        
        return {
            'id': obj.user.id,
            'username': f"{obj.user.first_name} {obj.user.last_name}",
            'avatar': avatar_url
        }

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    reactions = CommentReactionSerializer(many=True, read_only=True)
    current_user_reaction = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    reply_to_author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'lesson', 'author', 'parent', 'text',
            'comment_type', 'created_at', 'updated_at',
            'is_edited', 'replies', 'reactions',
            'likes_count', 'dislikes_count',
            'current_user_reaction', 'is_author',
            'reply_to_author'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at', 'is_edited']

    def get_author(self, obj):
        avatar_url = None
        if hasattr(obj.author, 'avatar_base64') and obj.author.avatar_base64:
            avatar_url = obj.author.avatar_base64
        
        return {
            'id': obj.author.id,
            'username': f"{obj.author.first_name} {obj.author.last_name}",
            'avatar': avatar_url
        }
        
    def get_reply_to_author(self, obj):
        """
        Get information about the author of the parent comment if this is a reply
        """
        if obj.parent and obj.parent.author:
            parent_author = obj.parent.author
            avatar_url = None
            if hasattr(parent_author, 'avatar_base64') and parent_author.avatar_base64:
                avatar_url = parent_author.avatar_base64
            
            return {
                'id': parent_author.id,
                'username': f"{parent_author.first_name} {parent_author.last_name}",
                'avatar': avatar_url
            }
        return None

    def get_replies(self, obj):
        """
        Get direct replies to this comment, sorted by creation date
        """
        if hasattr(obj, 'replies'):
            # Get direct replies only
            direct_replies = obj.replies.all().order_by('-created_at')
            
            # Use a separate serializer for replies to avoid infinite recursion
            serializer_context = {'request': self.context.get('request')}
            return CommentSerializer(direct_replies, many=True, context=serializer_context).data
        return []

    def get_current_user_reaction(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            reaction = obj.reactions.filter(user=request.user).first()
            if reaction:
                return reaction.reaction_type
        return None

    def get_is_author(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False

    def get_likes_count(self, obj):
        return obj.reactions.filter(reaction_type='LIKE').count()
    
    def get_dislikes_count(self, obj):
        return obj.reactions.filter(reaction_type='DISLIKE').count()

    def validate(self, data):
        # Validate comment_type
        comment_type = data.get('comment_type', 'COMMENT')
        if comment_type not in dict(Comment.COMMENT_TYPES):
            raise ValidationError({'comment_type': f"Invalid comment type. Choices are: {dict(Comment.COMMENT_TYPES).keys()}"})
        return data

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)   