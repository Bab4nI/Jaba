# backend/main/courses/admin.py

from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from unidecode import unidecode
from .models import Course, Module, Lesson


class BaseAdmin(admin.ModelAdmin):
    """Базовый класс с общими настройками"""

    list_per_page = 25
    save_on_top = True
    show_full_result_count = False


@admin.register(Course)
class CourseAdmin(BaseAdmin):
    list_display = (
        "title",
        "author",
        "is_published",
        "created_at",
        "thumbnail_preview",
    )
    list_editable = ("is_published",)
    list_filter = ("is_published", "created_at", "author")
    search_fields = ("title", "description", "slug")
    readonly_fields = ("thumbnail_preview", "slug", "created_at", "updated_at")
    raw_id_fields = ("author",)

    fieldsets = (
        (None, {"fields": ("title", "slug", "author", "description", "is_published")}),
        (
            "Обложка",
            {
                "fields": ("thumbnail", "thumbnail_preview"),
            },
        ),
        ("Даты", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            try:
                return mark_safe(
                    f'<img src="{obj.thumbnail.url}" style="max-height: 100px;"/>'
                )
            except:
                return "Ошибка загрузки изображения"
        return "Нет изображения"

    thumbnail_preview.short_description = "Превью обложки"

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = slugify(unidecode(obj.title))
        super().save_model(request, obj, form, change)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    search_fields = ("title", "description")
    ordering = ("course", "order")


@admin.register(Lesson)
class LessonAdmin(BaseAdmin):
    list_display = ("title", "module", "order", "duration", "thumbnail_list_preview")
    list_filter = ("module__course", "module")
    search_fields = ("title", "module__title")
    ordering = ("module", "order")
    readonly_fields = ("thumbnail_preview", "created_at", "updated_at")
    raw_id_fields = ("module",)

    fieldsets = (
        (None, {"fields": ("module", "title", "duration", "order")}),
        (
            "Обложка",
            {
                "fields": ("thumbnail", "thumbnail_preview"),
            },
        ),
        ("Даты", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def thumbnail_preview(self, obj):
        """Для страницы редактирования"""
        if obj.thumbnail:
            try:
                return mark_safe(
                    f'<img src="{obj.thumbnail.url}" style="max-height: 200px;"/>'
                )
            except:
                return "Ошибка загрузки"
        return "Нет обложки"

    thumbnail_preview.short_description = "Текущая обложка"

    def thumbnail_list_preview(self, obj):
        """Для списка уроков"""
        if obj.thumbnail:
            try:
                return mark_safe(
                    f'<img src="{obj.thumbnail.url}" style="max-height: 50px;"/>'
                )
            except:
                return "Ошибка"
        return "—"

    thumbnail_list_preview.short_description = "Обложка"