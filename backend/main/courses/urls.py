# main/courses/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet,
    ModuleViewSet,
    LessonViewSet,
    CodeExecutionView,
    MediaUploadView,
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

urlpatterns = [
    # Include the router URLs
    path("", include(router.urls)),
    # Form-specific paths
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
    path("execute-code/", CodeExecutionView.as_view(), name="execute-code"),
    path("upload-media/", MediaUploadView.as_view(), name="upload-media"),
]
