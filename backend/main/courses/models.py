from django.db import models
from django.conf import settings
from django.utils.text import slugify
from unidecode import unidecode
class Course(models.Model):
    """
    Основная модель курса.
    Содержит название, описание, автора и метаданные.
    """
    title = models.CharField(
        max_length=255,
        verbose_name="Название курса",
        help_text="Не более 255 символов"
    )
    slug = models.SlugField(
        max_length=300,
        unique=True,
        blank=True,
        verbose_name="URL-адрес курса",
        help_text="Автоматически генерируется из названия"
    )
    description = models.TextField(
        verbose_name="Описание",
        help_text="Полное описание курса"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Ссылка на кастомную модель пользователя
        on_delete=models.CASCADE,
        related_name="authored_courses",
        verbose_name="Автор"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name="Опубликован"
    )
    thumbnail = models.ImageField(
        upload_to="thumbnails/courses/",
        null=True,
        blank=True,
        verbose_name="Обложка курса"
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ["-created_at"]  # Сортировка по дате создания (новые первые)

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


class Module(models.Model):
    """
    Модуль курса. Связан с Course через ForeignKey.
    Порядок задается полем order для сортировки.
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules",
        verbose_name="Курс"
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Название модуля"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание модуля"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядковый номер",
        help_text="Определяет последовательность модулей в курсе"
    )

    class Meta:
        verbose_name = "Модуль"
        verbose_name_plural = "Модули"
        ordering = ["order"]  # Сортировка по полю order
        unique_together = [("course", "title")]  # Уникальность названия в рамках курса

    def __str__(self):
        return f"{self.course.title} → {self.title}"
    

class Lesson(models.Model):
    """
    Урок внутри модуля. Содержит контент (текст, видео, файлы).
    """
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Модуль"
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Название урока"
    )
    duration = models.PositiveIntegerField(
        default=0,
        verbose_name="Длительность (в минутах)",
        help_text="Для отображения прогресса"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок в модуле"
    )
    thumbnail = models.ImageField(
        upload_to="thumbnails/lessons/",
        null=True,
        blank=True,
        verbose_name="Обложка урока"
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
        """Возвращает контент урока, сгруппированный по типам."""
        return {
            'texts': self.contents.filter(content_type='TEXT'),
            'videos': self.contents.filter(content_type='VIDEO'),
            'images': self.contents.filter(content_type='IMAGE'),
            'gifs': self.contents.filter(content_type='GIF'),
            'files': self.contents.filter(content_type='FILE')
        }
    
class ContentBase(models.Model):
    """
    Абстрактная модель для всех типов контента урока.
    Поддерживает: текст, видео, файлы, изображения (включая GIF).
    """
    CONTENT_TYPES = [
        ('TEXT', 'Текст'),
        ('VIDEO', 'Видео'),
        ('IMAGE', 'Изображение'),
        ('GIF', 'GIF-анимация'),
        ('FILE', 'Файл'),
    ]

    lesson = models.ForeignKey(
        'Lesson',
        on_delete=models.CASCADE,
        related_name='contents',
        verbose_name='Урок'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок'
    )
    content_type = models.CharField(
        max_length=5,
        choices=CONTENT_TYPES,
        verbose_name='Тип контента'
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Заголовок'
    )
    text = models.TextField(
        blank=True,
        verbose_name='Текст',
        help_text='Для текстового контента'
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='Ссылка на видео'
    )
    image = models.ImageField(
        upload_to='contents/images/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )
    gif = models.FileField(
        upload_to='contents/gifs/',
        blank=True,
        null=True,
        verbose_name='GIF-анимация',
        help_text='Загрузите файл в формате .gif'
    )
    file = models.FileField(
        upload_to='contents/files/',
        blank=True,
        null=True,
        verbose_name='Файл'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['order']
        verbose_name = 'Базовый контент'
        verbose_name_plural = 'Базовый контент'

    def __str__(self):
        return f"{self.get_content_type_display()} → {self.title or 'Без названия'}"

class LessonContent(ContentBase):
    """
    Конкретная реализация контента урока.
    Наследует все поля от ContentBase.
    """
    class Meta(ContentBase.Meta):
        verbose_name = 'Контент урока'
        verbose_name_plural = 'Контент уроков'

    def clean(self):
        """Проверка, что выбран только один тип контента."""
        from django.core.exceptions import ValidationError
        
        fields = {
            'TEXT': self.text,
            'VIDEO': self.video_url,
            'IMAGE': self.image,
            'GIF': self.gif,
            'FILE': self.file
        }
        
        selected_fields = [k for k, v in fields.items() if v]
        if len(selected_fields) != 1:
            raise ValidationError("Выберите ровно один тип контента.")
        
        self.content_type = selected_fields[0]