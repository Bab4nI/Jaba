from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContentProgressViewSet

router = DefaultRouter()
router.register(r'content-progress', ContentProgressViewSet, basename='content-progress')

urlpatterns = [
    path('', include(router.urls)),
] 