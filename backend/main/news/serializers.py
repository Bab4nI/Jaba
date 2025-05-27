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
                # Если URL уже полный, возвращаем как есть
                if data['image_url'].startswith('http'):
                    return data
                # Иначе добавляем базовый URL
                data['image_url'] = request.build_absolute_uri(settings.MEDIA_URL + data['image_url'])
        return data

    def to_internal_value(self, data):
        if 'image_url' in data and data['image_url']:
            # Убираем базовый URL, если он есть
            if data['image_url'].startswith('http'):
                # Извлекаем только относительный путь после /media/
                parts = data['image_url'].split('/media/')
                if len(parts) > 1:
                    data['image_url'] = parts[1]
                else:
                    data['image_url'] = data['image_url'].split('/')[-1]
            # Убираем /media/ префикс, если он есть
            elif data['image_url'].startswith('/media/'):
                data['image_url'] = data['image_url'][7:]
        return super().to_internal_value(data) 