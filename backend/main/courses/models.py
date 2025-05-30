from django.db import models
from django.conf import settings
from django.utils.text import slugify
from unidecode import unidecode
from django.core.exceptions import ValidationError
import uuid
from django.utils import timezone


class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название курса")
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField(verbose_name="Описание")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_courses",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    thumbnail = models.ImageField(
        upload_to="thumbnails/courses/", null=True, blank=True
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            # Improved slug generation for Cyrillic characters
            # First try to transliterate Cyrillic to Latin
            base_slug = slugify(unidecode(self.title))

            # If slug is empty after transliteration (can happen with some Cyrillic characters),
            # use a more direct approach - just take the ID or use a random string
            if not base_slug:
                base_slug = str(uuid.uuid4())[:8]

            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @classmethod
    def find_by_slug(cls, slug_value):
        """
        Find a course by slug, regardless of case sensitivity.
        This helps with troubleshooting slug-related issues.
        """
        # First try exact match
        try:
            return cls.objects.get(slug=slug_value)
        except cls.DoesNotExist:
            # Try case-insensitive match
            courses = cls.objects.filter(slug__iexact=slug_value)
            if courses.exists():
                return courses.first()

            # Try partial match (contains)
            courses = cls.objects.filter(slug__contains=slug_value)
            if courses.exists():
                return courses.first()

            # No match found
            return None


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
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
        ("ARTICLE", "Статья"),
        ("LAB", "Лабораторная работа"),
        ("PRACTICE", "Практика"),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=LESSON_TYPES, default="ARTICLE")
    order = models.PositiveIntegerField(default=0)
    thumbnail = models.ImageField(
        upload_to="thumbnails/lessons/", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_datetime = models.DateTimeField(
        null=True, blank=True, help_text="Дата и время начала урока"
    )
    end_datetime = models.DateTimeField(
        null=True, blank=True, help_text="Дата и время окончания урока"
    )
    duration = models.PositiveIntegerField(default=0)  # Duration in minutes
    max_score = models.IntegerField(default=5)

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["order"]
        unique_together = [("module", "order")]

    def __str__(self):
        return self.title

    @property
    def is_available(self):
        now = timezone.now()
        if self.start_datetime and now < self.start_datetime:
            return False
        if self.end_datetime and now > self.end_datetime:
            return False
        return True

    def get_content(self):
        return {
            "texts": self.contents.filter(content_type="TEXT"),
            "videos": self.contents.filter(content_type="VIDEO"),
            "images": self.contents.filter(content_type="IMAGE"),
            "files": self.contents.filter(content_type="FILE"),
            "codes": self.contents.filter(content_type="CODE"),
            "quizzes": self.contents.filter(content_type="QUIZ"),
            "tables": self.contents.filter(content_type="TABLE"),
        }

    def save(self, *args, **kwargs):
        if not self.thumbnail:
            if self.type == "ARTICLE":
                self.thumbnail = "thumbnails/lessons/defaults/article.png"
            elif self.type == "LAB":
                self.thumbnail = "thumbnails/lessons/defaults/lab.png"
            elif self.type == "PRACTICE":
                self.thumbnail = "thumbnails/lessons/defaults/prac.png"
        super().save(*args, **kwargs)