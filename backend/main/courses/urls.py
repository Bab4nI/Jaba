from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, ModuleViewSet, LessonViewSet, LessonContentViewSet

# Инициализация роутера для ViewSets
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')

# Основные URL-паттерны приложения
urlpatterns = [
    # Включение URL-адресов из роутера (для CourseViewSet)
    path('', include(router.urls)),
    
    # URL для модулей курса
    path(
        'courses/<slug:course_slug>/modules/',
        ModuleViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='module-list'
    ),
    
    # URL для конкретного модуля
    path(
        'courses/<slug:course_slug>/modules/<int:pk>/',
        ModuleViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
        name='module-detail'
    ),
    
    # URL для уроков модуля
    path(
        'courses/<slug:course_slug>/modules/<int:module_id>/lessons/',
        LessonViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='lesson-list'
    ),
    
    # URL для конкретного урока
    path(
        'courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:pk>/',
        LessonViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
        name='lesson-detail'
    ),
    
    # URL для контента урока
    path(
        'courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/contents/',
        LessonContentViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='content-list'
    ),
    
    # URL для конкретного элемента контента
    path(
        'courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/contents/<int:pk>/',
        LessonContentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
        name='content-detail'
    ),
]