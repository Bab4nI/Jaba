from rest_framework import serializers
from .models import (
    Course,
    Module,
    Lesson,
)
from content.models import Content
from comments.models import Comment, CommentReaction
from rest_framework.exceptions import ValidationError
import logging
from django.shortcuts import get_object_or_404
from django.utils import timezone
import json

logger = logging.getLogger(__name__)

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = [
            'id',
            'order',
            'type',
            'content_data',
            'max_score',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

class LessonSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True, read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    time_remaining = serializers.SerializerMethodField()
    time_until_start = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "description",
            "content",
            "type",
            "module",
            "order",
            "thumbnail",
            "created_at",
            "updated_at",
            "start_datetime",
            "end_datetime",
            "duration",
            "is_available",
            "time_remaining",
            "time_until_start",
            "contents",
            "max_score",
        ]
        read_only_fields = ["created_at", "updated_at"]
        extra_kwargs = {
            "module": {"required": False},
            "duration": {"required": False, "default": 0},
            "max_score": {"required": False, "default": 0},
            "start_datetime": {"required": False},
            "end_datetime": {"required": False},
            "type": {"required": False, "default": "ARTICLE"},
            "content": {"required": False, "allow_blank": True},
            "description": {"required": False, "allow_blank": True},
            "thumbnail": {"required": False, "allow_null": True},
        }

    def get_time_remaining(self, obj):
        if not obj.end_datetime:
            return None
        now = timezone.now()
        if now > obj.end_datetime:
            return 0
        return (obj.end_datetime - now).total_seconds()

    def get_time_until_start(self, obj):
        if not obj.start_datetime:
            return None
        now = timezone.now()
        if now >= obj.start_datetime:
            return 0
        return (obj.start_datetime - now).total_seconds()

    def validate(self, data):
        module_id = self.context["view"].kwargs.get("module_id")
        if not module_id:
            raise serializers.ValidationError("Module ID is required")

        if "title" in data:
            qs = Lesson.objects.filter(module_id=module_id, title=data["title"])
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(
                    {"title": "Урок с таким названием уже существует в этом модуле"}
                )
        return data

    def create(self, validated_data):
        module_id = self.context["view"].kwargs["module_id"]
        module = get_object_or_404(Module, id=module_id)
        validated_data["module"] = module

        # Convert duration to integer if it's a string
        if "duration" in validated_data and isinstance(validated_data["duration"], str):
            validated_data["duration"] = int(validated_data["duration"])

        return super().create(validated_data)

    def update(self, instance, validated_data):
        thumbnail = validated_data.pop("thumbnail", None)

        if thumbnail is not None:
            if thumbnail == "":
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
        slug_field="slug", queryset=Course.objects.all(), write_only=True
    )

    class Meta:
        model = Module
        fields = [
            "id",
            "title",
            "description",
            "order",
            "course",
            "lessons",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "description": {"required": False, "allow_null": True},
            "course": {"write_only": True},
        }

    def validate(self, data):
        course = data.get("course")
        title = data.get("title")
        if course and title:
            qs = Module.objects.filter(course=course, title=title)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(
                    {"title": "Модуль с таким названием уже существует в этом курсе"}
                )
        return data


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "author",
            "thumbnail",
            "is_published",
            "modules",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "thumbnail": {"required": False, "allow_null": True},
            "description": {"required": False, "allow_null": True},
            "author": {"read_only": True},
            "slug": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }