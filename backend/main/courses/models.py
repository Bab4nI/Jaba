from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from unidecode import unidecode
import os
from django.core.exceptions import ValidationError

class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название курса")
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField(verbose_name="Описание")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_courses"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    thumbnail = models.ImageField(
        upload_to="thumbnails/courses/",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(unidecode(self.title))
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
        
    def lessons_count(self):
        """Общее количество уроков в курсе"""
        return Lesson.objects.filter(module__course=self).count()

    def get_user_progress(self, user):
        """Возвращает прогресс пользователя с аннотацией данных"""
        if not user.is_authenticated:
            return None
            
        return self.users_progress.filter(user=user).annotate(
            total_lessons=models.Count('course__modules__lessons', distinct=True),
            completed_lessons=models.Count(
                models.Case(
                    models.When(completed_lessons__is_completed=True, then=1),
                    output_field=models.IntegerField()
                ),
                distinct=True
            )
        ).first()

class Module(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Модуль"
        verbose_name_plural = "Модули"
        ordering = ["order"]
        unique_together = [("course", "title")]

    def __str__(self):
        return f"{self.course.title} → {self.title}"

class Lesson(models.Model):
    LESSON_TYPES = [
        ('ARTICLE', 'Статья'),
        ('LAB', 'Лабораторная работа'),
        ('PRACTICE', 'Практика'),
    ]

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="lessons"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)
    thumbnail = models.ImageField(
        upload_to="thumbnails/lessons/",
        null=True,
        blank=True
    )
    type = models.CharField(
        max_length=20,
        choices=LESSON_TYPES,
        default='ARTICLE'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["order"]
        unique_together = [("module", "title")]

    def __str__(self):
        return f"{self.module.title} → {self.title}"
    
    def get_content(self):
        return {
            'texts': self.contents.filter(content_type='TEXT'),
            'videos': self.contents.filter(content_type='VIDEO'),
            'images': self.contents.filter(content_type='IMAGE'),
            'files': self.contents.filter(content_type='FILE'),
            'codes': self.contents.filter(content_type='CODE'),
            'quizzes': self.contents.filter(content_type='QUIZ'),
            'tables': self.contents.filter(content_type='TABLE'),
        }

    def save(self, *args, **kwargs):
        if not self.thumbnail:
            if self.type == 'ARTICLE':
                self.thumbnail = 'thumbnails/lessons/defaults/article.png'
            elif self.type == 'LAB':
                self.thumbnail = 'thumbnails/lessons/defaults/lab.png'
            elif self.type == 'PRACTICE':
                self.thumbnail = 'thumbnails/lessons/defaults/prac.png'
        super().save(*args, **kwargs)
    
    def is_completed_by(self, user):
        """Проверяет, завершен ли урок пользователем"""
        if not user.is_authenticated:
            return False
        return LessonCompletion.objects.filter(
            progress__user=user,
            progress__course=self.module.course,
            lesson=self,
            is_completed=True
        ).exists()

class ContentBase(models.Model):
    CONTENT_TYPES = [
        ('TEXT', 'Текст'),
        ('VIDEO', 'Видео'),
        ('IMAGE', 'Изображение'),
        ('FILE', 'Файл'),
        ('CODE', 'Код'),
        ('QUIZ', 'Тест'),
        ('TABLE', 'Таблица'),
    ]

    lesson = models.ForeignKey(
        'Lesson',
        on_delete=models.CASCADE,
        related_name="contents"
    )
    order = models.PositiveIntegerField(default=0)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES)
    title = models.CharField(max_length=255, blank=True)
    text = models.TextField(blank=True)
    video_url = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='contents/images/', blank=True, null=True)
    file = models.FileField(upload_to='contents/files/', blank=True, null=True)
    code_language = models.CharField(max_length=50, blank=True)
    quiz_data = models.JSONField(default=dict, blank=True)
    table_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['order']

    def __str__(self):
        return f"{self.get_content_type_display()} → {self.title or 'Без названия'}"

    def clean(self):
        # Validate based on the provided content_type
        if not self.content_type:
            raise ValidationError("Необходимо указать тип контента.")

        # Define required fields for each content type
        validation_rules = {
            'TEXT': {'required': ['text'], 'optional': ['title']},
            'VIDEO': {'required': ['video_url'], 'optional': ['title']},
            'IMAGE': {'required': ['image'], 'optional': ['title']},
            'FILE': {'required': ['file'], 'optional': ['title']},
            'CODE': {'required': ['text', 'code_language'], 'optional': ['title']},
            'QUIZ': {'required': ['quiz_data'], 'optional': ['title']},
            'TABLE': {'required': ['table_data'], 'optional': ['title']},
        }

        rules = validation_rules.get(self.content_type)
        if not rules:
            raise ValidationError(f"Недопустимый тип контента: {self.content_type}")

        # Check required fields
        errors = {}
        for field in rules['required']:
            value = getattr(self, field)
            if field == 'quiz_data':
                if not value.get('question') or not value.get('answers') or len(value.get('answers', [])) < 2:
                    errors['quiz_data'] = "Вопрос и минимум два ответа обязательны для теста."
            elif field == 'table_data':
                if not value.get('headers') or not value.get('data'):
                    errors['table_data'] = "Заголовки и данные таблицы обязательны."
            elif not value:
                errors[field] = f"Поле {field} обязательно для типа {self.content_type}."

        # Ensure non-relevant fields are empty
        all_fields = ['text', 'video_url', 'image', 'file', 'code_language', 'quiz_data', 'table_data']
        relevant_fields = rules['required'] + rules['optional']
        for field in all_fields:
            if field not in relevant_fields and getattr(self, field):
                errors[field] = f"Поле {field} не должно быть заполнено для типа {self.content_type}."

        if errors:
            raise ValidationError(errors)

class LessonContent(ContentBase):
    class Meta(ContentBase.Meta):
        verbose_name = 'Контент урока'
        verbose_name_plural = 'Контент уроков'












class UserCourseProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_progress'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='users_progress'
    )
    started_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_lesson = models.ForeignKey(
        'Lesson',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'course'],
                name='unique_user_course_progress'
            )
        ]

    def update_completion(self):
        """Обновляет статус завершения курса"""
        total = self.course.lessons_count()
        completed = self.completed_lessons.filter(is_completed=True).count()
        
        if total > 0 and completed >= total:
            self.is_completed = True
            self.completed_at = timezone.now()
        else:
            self.is_completed = False
            self.completed_at = None
        self.save()

    def completion_percentage(self):
        if hasattr(self, 'total_lessons') and hasattr(self, 'completed_lessons'):
            total = self.total_lessons
            completed = self.completed_lessons
        else:
            total = self.course.lessons_count()
            completed = self.completed_lessons.filter(is_completed=True).count()
            
        return round((completed / total) * 100) if total > 0 else 0

class LessonCompletion(models.Model):
    progress = models.ForeignKey(
        UserCourseProgress,
        on_delete=models.CASCADE,
        related_name='completed_lessons'
    )
    lesson = models.ForeignKey(
        'Lesson',
        on_delete=models.CASCADE,
        related_name='user_completions'
    )
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(default=timezone.now)
    score = models.PositiveSmallIntegerField(null=True, blank=True, default=0)
    attempts = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['progress', 'lesson'],
                name='unique_lesson_completion'
            )
        ]

    def clean(self):
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
        if self.is_completed:
            self.attempts += 1

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.progress.update_completion()