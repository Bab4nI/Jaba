# backend/main/courses/admin.py

from django.contrib import admin
from .models import Course, Module, Lesson, UserCourseProgress, LessonCompletion

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'module')

@admin.register(UserCourseProgress)
class UserCourseProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'progress_percent')
    list_filter = ('course', 'is_completed')
    search_fields = ('user__username', 'course__title')

    def progress_percent(self, obj):
        return f"{obj.completion_percentage()}%"
    progress_percent.short_description = 'Progress (%)'

@admin.register(LessonCompletion)
class LessonCompletionAdmin(admin.ModelAdmin):
    list_display = ('id', 'progress', 'lesson', 'is_completed', 'score', 'attempts', 'completed_at')
    list_filter = ('is_completed',)
    search_fields = ('progress__user__username', 'lesson__title')
