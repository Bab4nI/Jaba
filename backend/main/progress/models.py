from django.db import models
from django.conf import settings
from content.models import Content

class ContentProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    user_answer = models.JSONField(default=dict)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'content')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.content.type} - Score: {self.score}" 