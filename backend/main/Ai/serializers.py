from rest_framework import serializers
from .models import (
    AIChatState,
)
import logging


logger = logging.getLogger(__name__)

class AIChatStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIChatState
        fields = ["id", "lesson", "is_enabled", "updated_at"]
        read_only_fields = ["updated_at"]
