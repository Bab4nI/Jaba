# main/courses/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CommentViewSet,
    CommentReactionViewSet,
)

# Use trailing_slash=True to match Django's default behavior
router = DefaultRouter(trailing_slash=True)
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

urlpatterns = [
    # Include the router URLs
    path("", include(router.urls)),
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
]
