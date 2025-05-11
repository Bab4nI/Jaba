# backend/main/courses/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LessonCompletion, UserCourseProgress, Lesson

@receiver(post_save, sender=LessonCompletion)
def update_course_progress(sender, instance, **kwargs):
    """
    Обработчик сигнала для обновления прогресса курса, когда завершен урок.
    """
    instance.progress.update_completion()

@receiver(post_save, sender=UserCourseProgress)
def init_lesson_completions(sender, instance, created, **kwargs):
    """
    Обработчик сигнала для инициализации завершений уроков при создании прогресса курса.
    """
    if created:
        lessons = Lesson.objects.filter(module__course=instance.course)
        LessonCompletion.objects.bulk_create([
            LessonCompletion(progress=instance, lesson=lesson)
            for lesson in lessons
        ])
