# main/courses/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AIChatView,
    AIChatStateViewSet,
)

# Use trailing_slash=True to match Django's default behavior
router = DefaultRouter(trailing_slash=True)
router.register(
    r"lessons/(?P<lesson_id>\d+)/ai-chat-state",
    AIChatStateViewSet,
    basename="ai-chat-state",
)

urlpatterns = [
    # Include the router URLs
    path("", include(router.urls)),
    # Form-specific paths
    path("ai-chat/", AIChatView.as_view(), name="ai-chat"),
]
