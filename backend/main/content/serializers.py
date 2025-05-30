from rest_framework import serializers
from .models import Content, CustomForm
from progress.models import ContentProgress
import json

class ContentSerializer(serializers.ModelSerializer):
    user_score = serializers.SerializerMethodField()
    user_answer = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = ['id', 'type', 'order', 'max_score', 'content_data', 
                 'user_score', 'user_answer', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(data['content_data'], str):
            try:
                data['content_data'] = json.loads(data['content_data'])
            except json.JSONDecodeError:
                data['content_data'] = {}
        return data

    def get_user_score(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = ContentProgress.objects.get(user=request.user, content=obj)
                return progress.score
            except ContentProgress.DoesNotExist:
                return 0
        return 0

    def get_user_answer(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = ContentProgress.objects.get(user=request.user, content=obj)
                return progress.user_answer
            except ContentProgress.DoesNotExist:
                return {}
        return {}

class CustomFormSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True, read_only=True)

    class Meta:
        model = CustomForm
        fields = ['id', 'title', 'contents', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
