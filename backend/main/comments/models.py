from django.db import models
from django.conf import settings
from django.utils.text import slugify
from unidecode import unidecode
from django.core.exceptions import ValidationError
import uuid
from django.utils import timezone
from django.contrib.auth import get_user_model
from courses.models import Lesson

User = get_user_model()

# Create your models here.
class Comment(models.Model):
    COMMENT_TYPES = [
        ("COMMENT", "Комментарий"),
        ("SOLUTION", "Решение"),
    ]

    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    text = models.TextField()
    comment_type = models.CharField(
        max_length=20, choices=COMMENT_TYPES, default="COMMENT"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    likes_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.lesson.title}"

    def update_likes_count(self):
        self.likes_count = self.reactions.filter(reaction_type="LIKE").count()
        self.save(update_fields=["likes_count"])


class CommentReaction(models.Model):
    REACTION_TYPES = [
        ("LIKE", "Нравится"),
        ("DISLIKE", "Не нравится"),
    ]

    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="reactions"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comment_reactions",
    )
    reaction_type = models.CharField(max_length=10, choices=REACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Реакция на комментарий"
        verbose_name_plural = "Реакции на комментарии"
        unique_together = [("comment", "user")]

    def __str__(self):
        return f"{self.user.username} {self.reaction_type} → {self.comment}"