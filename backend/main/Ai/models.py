from django.db import models
from courses.models import Lesson

# Create your models here.
class AIChatState(models.Model):
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="ai_chat_states"
    )
    is_enabled = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Состояние AI чата"
        verbose_name_plural = "Состояния AI чата"

    def __str__(self):
        return f"{self.lesson.title} - AI Chat: {'Enabled' if self.is_enabled else 'Disabled'}"