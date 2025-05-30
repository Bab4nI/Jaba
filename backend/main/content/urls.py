from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContentViewSet, CustomFormViewSet

router = DefaultRouter()
router.register(r'contents', ContentViewSet, basename='content')
router.register(r'forms', CustomFormViewSet, basename='form')

urlpatterns = [
    path('', include(router.urls)),
]
