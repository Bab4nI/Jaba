# main/courses/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet,
    ModuleViewSet,
    LessonViewSet,
    LessonContentViewSet,
    CommentViewSet,
    CommentReactionViewSet,
    CodeExecutionView,
    AIChatView,
    MediaUploadView,
    UserProgressViewSet,
    CustomFormViewSet,
    AIChatStateViewSet,
)

# Use trailing_slash=True to match Django's default behavior
router = DefaultRouter(trailing_slash=True)
router.register(r"courses", CourseViewSet, basename="course")
router.register(
    r"courses/(?P<course_slug>[^/.]+)/modules", ModuleViewSet, basename="module"
)
router.register(
    r"courses/(?P<course_slug>[^/.]+)/modules/(?P<module_id>\d+)/lessons",
    LessonViewSet,
    basename="lesson",
)
router.register(
    r"courses/(?P<course_slug>[^/.]+)/modules/(?P<module_id>\d+)/lessons/(?P<lesson_id>\d+)/contents",
    LessonContentViewSet,
    basename="lesson-content",
)
router.register(
    r"courses/(?P<course_slug>[^/.]+)/modules/(?P<module_id>\d+)/lessons/(?P<lesson_id>\d+)/comments",
    CommentViewSet,
    basename="comment",
)
router.register(
    r"courses/(?P<course_slug>[^/.]+)/modules/(?P<module_id>\d+)/lessons/(?P<lesson_id>\d+)/comments/(?P<comment_id>\d+)/reactions",
    CommentReactionViewSet,
    basename="comment-reaction",
)
router.register(
    r"courses/(?P<course_slug>[^/.]+)/modules/(?P<module_id>\d+)/lessons/(?P<lesson_id>\d+)/forms",
    CustomFormViewSet,
    basename="form",
)
router.register(r"progress", UserProgressViewSet, basename="progress")
router.register(
    r"lessons/(?P<lesson_id>\d+)/ai-chat-state",
    AIChatStateViewSet,
    basename="ai-chat-state",
)

urlpatterns = [
    # Include the router URLs
    path("", include(router.urls)),
    # Form-specific paths
    path(
        "courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/forms/",
        CustomFormViewSet.as_view({"get": "list", "post": "create"}),
        name="form-list",
    ),
    path(
        "courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/forms/<int:pk>/",
        CustomFormViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="form-detail",
    ),
    # Add explicit course list endpoint with POST support
    path(
        "courses/",
        CourseViewSet.as_view({"get": "list", "post": "create"}),
        name="course-list-with-slash",
    ),
    path(
        "courses",
        CourseViewSet.as_view({"get": "list", "post": "create"}),
        name="course-list-no-slash",
    ),
    # Add explicit course detail endpoints
    path(
        "courses/<slug:slug>/",
        CourseViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="course-detail-with-slash",
    ),
    path(
        "courses/<slug:slug>",
        CourseViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="course-detail-no-slash",
    ),
    path(
        "courses/<slug:course_slug>/modules/",
        ModuleViewSet.as_view({"get": "list", "post": "create"}),
        name="module-list",
    ),
    path(
        "courses/<slug:course_slug>/modules/<int:pk>/",
        ModuleViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="module-detail",
    ),
    path(
        "courses/<slug:course_slug>/modules/<int:module_id>/lessons/",
        LessonViewSet.as_view({"get": "list", "post": "create"}),
        name="lesson-list",
    ),
    path(
        "courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:pk>/",
        LessonViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="lesson-detail",
    ),
    path(
        "courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/contents/",
        LessonContentViewSet.as_view({"get": "list", "post": "create"}),
        name="content-list",
    ),
    path(
        "courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/contents/<int:pk>/",
        LessonContentViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="content-detail",
    ),
    path(
        "courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/contents/order/",
        LessonContentViewSet.as_view({"patch": "update_order"}),
        name="content-order",
    ),
    path(
        "courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/comments/",
        CommentViewSet.as_view({"get": "list", "post": "create"}),
        name="lesson-comments",
    ),
    path(
        "courses/<slug:course_slug>/modules/<int:module_id>/lessons/<int:lesson_id>/comments/<int:pk>/",
        CommentViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="comment-detail",
    ),
    path("comments/", CommentViewSet.as_view({"get": "list"}), name="comments-list"),
    path(
        "comments/<int:pk>/",
        CommentViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="comment-direct",
    ),
    path(
        "comments/<int:comment_id>/reactions/",
        CommentReactionViewSet.as_view({"get": "list", "post": "create"}),
        name="comment-reactions",
    ),
    path(
        "comments/<int:comment_id>/reactions/<int:pk>/",
        CommentReactionViewSet.as_view({"get": "retrieve", "delete": "destroy"}),
        name="reaction-detail",
    ),
    path(
        "comments/<int:comment_id>/user-reaction/",
        CommentReactionViewSet.as_view({"delete": "delete_user_reaction"}),
        name="delete-user-reaction",
    ),
    path("execute-code/", CodeExecutionView.as_view(), name="execute-code"),
    path("ai-chat/", AIChatView.as_view(), name="ai-chat"),
    path("upload-media/", MediaUploadView.as_view(), name="upload-media"),
    # Add progress-specific paths
    path(
        "courses/<slug:course_slug>/progress/",
        UserProgressViewSet.as_view({"get": "course_progress"}),
        name="course-progress",
    ),
    path(
        "student-progress/",
        UserProgressViewSet.as_view({"get": "student_progress"}),
        name="student-progress",
    ),
    path(
        "lessons/<int:lesson_id>/progress/",
        UserProgressViewSet.as_view({"get": "lesson_progress"}),
        name="lesson-progress",
    ),
    path(
        "lessons/<int:lesson_id>/mark-completed/",
        UserProgressViewSet.as_view({"post": "mark_completed"}),
        name="mark-lesson-completed",
    ),
    path(
        "lessons/<int:lesson_id>/reset-progress/",
        UserProgressViewSet.as_view({"post": "reset_progress"}),
        name="reset-lesson-progress",
    ),
    path("groups/", UserProgressViewSet.as_view({"get": "groups"}), name="groups-list"),
    path(
        "group-statistics/",
        UserProgressViewSet.as_view({"get": "group_statistics"}),
        name="group-statistics",
    ),
    path(
        "lesson-contents/<int:pk>/submit-answer/",
        LessonContentViewSet.as_view({"post": "submit_answer"}),
        name="submit-content-answer",
    ),
]
