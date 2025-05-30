from rest_framework import serializers
from .models import ContentProgress

class ContentProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentProgress
        fields = ['id', 'score', 'user_answer', 'completed', 'created_at', 'updated_at', 'content_id', 'user_id']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_id'] 