# main/courses/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, ModuleViewSet, LessonViewSet, LessonContentViewSet, CodeExecutionView, AIChatView

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')

urlpatterns = [
    path('', include(router.urls)),
    
    path(
        'courses/<slug:course_slug>/modules/',
        ModuleViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='module-list'
    ),
    
    path(
        'courses/<slug:course_slug>/modules/<int:pk>/',
        ModuleViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='module-detail'
    ),
    
    path(
        'courses/<slug:course_slug>/modules/<int:module_id>/lessons/',
        LessonViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='lesson-list'
    ),
    
    path(
        'courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:pk>/',
        LessonViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='lesson-detail'
    ),
    
    path(
        'courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/contents/',
        LessonContentViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='content-list'
    ),
    
    path(
        'courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/contents/<int:pk>/',
        LessonContentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='content-detail'
    ),
    
    path(
        'courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/contents/order/',
        LessonContentViewSet.as_view({'patch': 'update_order'}),
        name='content-order'
    ),

    path('execute-code/', CodeExecutionView.as_view(), name='execute-code'),
    path('ai/chat/', AIChatView.as_view(), name='ai-chat'),
]