from rest_framework import serializers
from django.conf import settings
from .models import News

class NewsSerializer(serializers.ModelSerializer):
    image_url = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'date', 'link', 'image_url']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data['image_url']:
            request = self.context.get('request')
            if request:
                data['image_url'] = request.build_absolute_uri(settings.MEDIA_URL + data['image_url'])
        return data

    def to_internal_value(self, data):
        # Если image_url начинается с /media/, убираем этот префикс
        if 'image_url' in data and data['image_url'] and data['image_url'].startswith('/media/'):
            data['image_url'] = data['image_url'][7:]  # Убираем '/media/' из начала
        return super().to_internal_value(data) 