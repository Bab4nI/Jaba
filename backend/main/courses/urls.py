# main/courses/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, ModuleViewSet, LessonViewSet,
    LessonContentViewSet, CommentViewSet, CommentReactionViewSet,
    CodeExecutionView, AIChatView, MediaUploadView
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'modules', ModuleViewSet, basename='module')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'lesson-contents', LessonContentViewSet, basename='lesson-content')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'comment-reactions', CommentReactionViewSet, basename='comment-reaction')

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

    path(
        'courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/comments/',
        CommentViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='lesson-comments'
    ),
    path(
        'courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/comments/<int:pk>/',
        CommentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='comment-detail'
    ),
    
    path(
        'comments/',
        CommentViewSet.as_view({'get': 'list'}),
        name='comments-list'
    ),
    path(
        'comments/<int:pk>/',
        CommentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='comment-direct'
    ),
    
    path(
        'comments/<int:comment_id>/reactions/',
        CommentReactionViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='comment-reactions'
    ),
    path(
        'comments/<int:comment_id>/reactions/<int:pk>/',
        CommentReactionViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}),
        name='reaction-detail'
    ),
    path(
        'comments/<int:comment_id>/user-reaction/',
        CommentReactionViewSet.as_view({'delete': 'delete_user_reaction'}),
        name='delete-user-reaction'
    ),

    path('execute-code/', CodeExecutionView.as_view(), name='execute-code'),
    path('ai/chat/', AIChatView.as_view(), name='ai-chat'),
    path('upload/', MediaUploadView.as_view(), name='media-upload'),
]