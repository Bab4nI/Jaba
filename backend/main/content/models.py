from django.db import models
from django.conf import settings
from courses.models import Lesson

class Content(models.Model):
    CONTENT_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('code', 'Code'),
        ('quiz', 'Quiz'),
        ('table', 'Table'),
        ('file', 'File'),
        ('fillin', 'Fill In'),
    )

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='content_items')
    type = models.CharField(max_length=10, choices=CONTENT_TYPES)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Common fields for all content types
    max_score = models.IntegerField(default=1)
    
    # Type-specific fields stored as JSON
    content_data = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['order']
        unique_together = ['lesson', 'order']

    def __str__(self):
        return f"{self.get_type_display()} - {self.lesson.title}"

class CustomForm(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='custom_forms')
    title = models.CharField(max_length=255, blank=True)
    contents = models.ManyToManyField(Content, related_name='forms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Form: {self.title} - {self.lesson.title}" 